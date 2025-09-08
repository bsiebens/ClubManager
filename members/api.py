from ninja import ModelSchema, Router

from .models import Member

router = Router()


class MemberSchema(ModelSchema):
    first_name: str
    last_name: str

    class Meta:
        model = Member
        fields = ["id"]

    @staticmethod
    def resolve_first_name(obj: Member) -> str:
        return obj.user.first_name

    @staticmethod
    def resolve_last_name(obj: Member) -> str:
        return obj.user.last_name


@router.get("/", response=list[MemberSchema])
def members(request):
    return Member.objects.all()
