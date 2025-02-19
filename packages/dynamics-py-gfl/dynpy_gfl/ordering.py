from dataclasses import dataclass

from django.db.models import Expression, F

from dynpy_gfl import constants
from dynpy_gfl.enums import FilterListOrder


@dataclass
class OrderHelper:
    ASC: Expression
    DESC: Expression


class FieldOrderByClause:
    def __init__(self, field, order):
        self.field = field
        self.order = order

    def process_field(self):
        match self.field:
            case str():
                value = (
                    F(self.field).desc() if self.order == FilterListOrder.DESC else F(self.field).asc()
                )
            case dict():
                value = self.field.get(self._get_order_as_ASC_or_DESC(self.order))
            case OrderHelper():
                value = getattr(self.field, self._get_order_as_ASC_or_DESC(self.order))

        if not isinstance(value, Expression):
            raise TypeError("Value must be an Expression object. I.e F('field_name').desc() .")
        return value

    def _get_order_as_ASC_or_DESC(self, order):
        return constants.ASC if order == FilterListOrder.ASC else constants.DESC
