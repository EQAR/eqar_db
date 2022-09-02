from datetime import date

from django.core.exceptions import ValidationError

def validate_date_in_past(value):
    if value > date.today():
        raise ValidationError("This date must not be in the future.")

