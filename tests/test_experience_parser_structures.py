from parsers.experience_parser import ExperienceParser


parser = ExperienceParser()


TEST_CASES = {
    "marketing": """\
PROFESSIONAL EXPERIENCE
Marketing Intern
May 20xx – September 20xx
FirstService Residential
New York, NY
Researched and identified 10 influential social media accounts and influencers
Marketing Communications Intern
May 20xx– September 20xx
Lify+
Created weekly PowerPoint presentations for internal and external use
""",

    "tax": """\
RELEVANT EXPERIENCE
June – September 20XX
Accounting Assistant Intern
Windfall Corporation – Indianapolis, IN
Reconciled bank statements and accounts payable/receivable records
January – June 20XX
Tax Preparation Volunteer
Volunteer Income Tax Assistant (VITA) – Bloomington, IN
Prepared tax returns for 25 low-income individuals and families
September 20XX – Present
Vice President, Accounting Society
Indiana University – Bloomington, IN
Collaborate with executive board to plan and execute events
""",

    "software": """\
PROFESSIONAL EXPERIENCE
Summer 20XX
Briggs–Henson Software Inc., Baton Rouge, LA
Software Engineering Intern
Collaborated with a team of developers to build a REST API
Pineapple Systems Inc., Baton Rouge, LA
Worked with a team of developers to develop a Django-based web application
"""
}


for name, text in TEST_CASES.items():

    print("\n" + "=" * 70)
    print(name.upper())
    print("=" * 70)

    lines = [
        parser.normalize_line(line)
        for line in text.splitlines()
        if parser.normalize_line(line)
    ]

    print("\nDATE DETECTION:")

    for line in lines:
        print(
            f"{line!r} -> "
            f"{parser.is_date_line(line)}"
        )

    print("\nTITLE DETECTION:")

    for line in lines:
        print(
            f"{line!r} -> "
            f"{parser.looks_like_title(line)}"
        )

    print("\nCOMPANY DETECTION:")

    for line in lines:
        print(
            f"{line!r} -> "
            f"{parser.looks_like_company(line)}"
        )

    print("\nDATE PARSING:")

    for line in lines:
        if parser.is_date_line(line):
            print(
                line,
                "=>",
                parser.parse_date_range(line)
            )

    print("\nRECORDS:")

    records = parser.parse_records(lines)

    for record in records:
        print(
            {
                "title": record.get("job_title"),
                "company": record.get("company"),
                "location": record.get("location"),
                "start_text": record.get("start_date_text"),
                "end_text": record.get("end_date_text"),
                "responsibilities": len(
                    record.get("responsibilities", [])
                ),
            }
        )