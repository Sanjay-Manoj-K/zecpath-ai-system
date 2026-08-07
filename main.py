from parsers.resume_text_extractor import extract_resume_text


def main():

    file_path = "data/resumes/ai-developer-resume.docx"

    text = extract_resume_text(file_path)

    print("\n========================")
    print(text)
    print("========================")


if __name__ == "__main__":
    main()