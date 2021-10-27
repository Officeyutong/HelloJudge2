from typing import ClassVar, Type
from marshmallow_dataclass import dataclass
from common.schema import GeneralUserEntry
from marshmallow import Schema


# @dataclass
# class SolutionListEntry:
#     content: str
#     uid: int
#     username: str
#     email: str
#     release_timestamp: int
#     verified_timestamp: int
#     Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class RouteSolutionEntry:
    content: str
    problem_id: int
    Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class RouteSolutionListEntrySchema:
    id: int
    uploader: GeneralUserEntry
    content: str
    top: bool
    verified: bool
    upload_timestamp: int
    verifier: GeneralUserEntry
    verify_timestamp: int
    Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class RouteAdminSubmitSolutionSchema:
    content: str
    top: bool
    problem_id: int
    Schema: ClassVar[Type[Schema]] = Schema


route_solution_entry_schema = RouteSolutionEntry.Schema()
