import openpyxl

from django.core.exceptions import ValidationError


REQUIRED_COLUMNS = {
    "student number",
    "full name",
}


def normalize_column(value):
    return str(value).strip().lower()


def parse_excel(file):
    try:
        workbook = openpyxl.load_workbook(
            file,
            read_only=True,
            data_only=True,
        )

        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)

        # Get header row
        headers = next(rows, None)

        if not headers:
            raise ValidationError(
                "The Excel file is empty."
            )

        # Normalize headers
        normalized_headers = [
            normalize_column(header)
            for header in headers
            if header is not None
        ]

        # File must contain exactly these two columns
        if set(normalized_headers) != REQUIRED_COLUMNS:
            raise ValidationError(
                "Invalid columns. The file must contain exactly "
                "'Student Number' and 'Full Name'."
            )

        # Find the position of each column
        try:
            student_number_index = normalized_headers.index(
                "student number"
            )

            full_name_index = normalized_headers.index(
                "full name"
            )

        except ValueError:
            raise ValidationError(
                "The file must contain 'Student Number' "
                "and 'Full Name' columns."
            )

        students = []

        # Track duplicate student numbers
        seen_numbers = set()

        # Process student rows
        for row_number, row in enumerate(rows, start=2):

            # Ignore completely empty rows
            if not any(value is not None for value in row):
                continue

            # Check that the row contains both columns
            if len(row) <= max(
                student_number_index,
                full_name_index,
            ):
                raise ValidationError(
                    f"Row {row_number}: "
                    "The row does not contain all required columns."
                )

            student_number = row[student_number_index]
            full_name = row[full_name_index]

            # Student number is required
            if (
                student_number is None
                or not str(student_number).strip()
            ):
                raise ValidationError(
                    f"Row {row_number}: "
                    "Student Number is required."
                )

            # Full name is required
            if (
                full_name is None
                or not str(full_name).strip()
            ):
                raise ValidationError(
                    f"Row {row_number}: "
                    "Full Name is required."
                )

            registration_number = str(
                student_number
            ).strip()

            # Check duplicate within uploaded file
            if registration_number in seen_numbers:
                raise ValidationError(
                    f"Row {row_number}: Duplicate Student Number "
                    f"'{registration_number}' in this file."
                )

            seen_numbers.add(registration_number)

            students.append({
                "registration_number": registration_number,
                "full_name": str(full_name).strip(),
            })

        # At least one student must exist
        if not students:
            raise ValidationError(
                "The file does not contain any students."
            )

        return students

    except ValidationError:
        raise

    except Exception as e:
        raise ValidationError(
            f"Could not read the Excel file: {str(e)}"
        )
