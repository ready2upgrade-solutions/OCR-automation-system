from models.structures import SemanticFact

def classify_row(row, sibling_rows=None):
    atoms = sorted(row.atoms, key=lambda a: a.x0)

    if len(atoms) == 1:
        return "TEXT"

    gaps = horizontal_gaps(atoms)
    max_gap = max(gaps) if gaps else 0
    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    x_centers = [a.x_center for a in atoms]
    x_spread = max(x_centers) - min(x_centers)

    # KEY–VALUE: one dominant gap
    if max_gap > 3 * avg_gap and max_gap > 40:
        return "KEY_VALUE"

    # TABLE: column alignment with neighbors
    if sibling_rows:
        aligned_columns = 0
        for sib in sibling_rows:
            if len(sib.atoms) == len(atoms):
                aligned_columns += 1

        if aligned_columns >= 2:
            return "TABLE"

    # Otherwise → paragraph / heading / bullet
    return "TEXT"

def build_semantics(rows):
    facts = []
    text_blocks = []

    for idx, row in enumerate(rows):
        siblings = rows[max(0, idx-2): idx+3]
        row_type = classify_row(row, siblings)
        atoms = sorted(row.atoms, key=lambda a: a.x0)

        joined_text = " ".join(a.text for a in atoms)

        if row_type == "KEY_VALUE":
            gaps = horizontal_gaps(atoms)
            split_index = gaps.index(max(gaps)) + 1

            label = " ".join(a.text for a in atoms[:split_index])
            value = " ".join(a.text for a in atoms[split_index:])

            facts.append({
                "page": row.page,
                "label": label,
                "value": value
            })

        elif row_type == "TABLE":
            text_blocks.append({
                "page": row.page,
                "type": "table_row",
                "cells": [a.text for a in atoms]
            })

        else:
            text_blocks.append({
                "page": row.page,
                "type": "text",
                "text": joined_text
            })

    return facts, text_blocks


def horizontal_gaps(atoms):
    atoms = sorted(atoms, key=lambda a: a.x0)
    gaps = []

    for i in range(len(atoms) - 1):
        gap = atoms[i+1].x0 - atoms[i].x1
        gaps.append(gap)

    return gaps
