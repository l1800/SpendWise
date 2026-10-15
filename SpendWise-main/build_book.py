# -*- coding: utf-8 -*-
"""בונה את ספר הפרויקט השלם — קובץ Word אחד."""

from docx import Document

import build_book_docx as kit
from book_part_a import cover, toc, intro, proposal
from book_part_b import body_intro, goals, market, spec
from book_part_c import algorithm
from book_part_d import architecture, models_chapter
from book_part_e import classes, technologies


def main():
    doc = Document()
    kit.setup(doc)

    # חלק א׳ — שער, תוכן עניינים, תקציר, הצעת הפרויקט
    cover(doc)
    toc(doc)
    intro(doc)
    proposal(doc)

    # חלק ב׳ — מבוא, מטרות, רקע תיאורטי, אפיון
    body_intro(doc)
    goals(doc)
    market(doc)
    spec(doc)

    # חלק ג׳ — האלגוריתם המרכזי
    algorithm(doc)

    # חלק ד׳ — ארכיטקטורה, מודלים
    architecture(doc)
    models_chapter(doc)

    # חלק ה׳ — מחלקות, טכנולוגיות
    classes(doc)
    technologies(doc)

    doc.save(kit.OUT)
    print("נשמר:", kit.OUT)


if __name__ == "__main__":
    main()
