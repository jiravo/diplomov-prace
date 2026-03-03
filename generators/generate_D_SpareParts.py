import pandas as pd


def generate_D_SparePart():

    data = [
        # ---------------- Spotřební ----------------
        (1, "Ložisko malé", 1800, 15, 22),
        (2, "Řemen pohonu", 2400, 12, 9),  # POD MINIMEM
        (3, "Filtr oleje", 900, 20, 30),
        (4, "Filtr vzduchu", 1200, 18, 14),  # POD MINIMEM
        (5, "Snímač polohy", 3500, 10, 14),
        (6, "Teplotní čidlo", 4200, 8, 12),
        (7, "Tlakový snímač", 4800, 8, 6),  # POD MINIMEM
        (8, "Bezpečnostní spínač", 3200, 10, 15),
        # ---------------- Střední ----------------
        (9, "Hydraulický ventil", 12500, 6, 8),
        (10, "Malý servomotor", 18500, 4, 6),
        (11, "Frekvenční měnič", 22000, 3, 5),
        (12, "Pohon dopravníku", 19500, 4, 3),  # POD MINIMEM
        (13, "Elektronický modul řízení", 16000, 5, 7),
        (14, "Napájecí zdroj", 9800, 6, 9),
        (15, "Reléová jednotka", 8700, 6, 10),
        # ---------------- Větší komponenty ----------------
        (16, "Hydraulické čerpadlo", 42000, 2, 3),
        (17, "Velký servomotor", 55000, 1, 2),
        (18, "Řídicí jednotka PLC", 60000, 1, 1),
        (19, "Výkonový modul", 38000, 2, 3),
        (20, "Chladicí jednotka", 47000, 1, 2),
    ]

    df = pd.DataFrame(
        data,
        columns=[
            "part_id",
            "part_name",
            "cost_per_unit",
            "minimum_stock",
            "current_stock",
        ],
    )

    df.to_csv("data/BI/D_SparePart.csv", index=False)

    return df
