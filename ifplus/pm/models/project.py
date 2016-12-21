# -*- coding: utf-8 -*-
from ifplus.vfs.models.file import FileObject


class PlanVersion(object):
    pass


class PlanArchive(object):
    pass


class Scenario(object):
    pass


class Baseline(object):
    pass


# -ID
# - Name
# - Description
# - Comment
# - Objective
# - Activities
# - Conditions
# - Dependencies
# - StartDate
# - EndDate
# - LatestStartDate
# - EarliestStartDate
# - LatestEndDate
# - EarliestEndDate
# - Effort
# - Float
# - Duration
# - Risk
# - PostponedUntil
# - Priority
# - ResourcePlanningType
# - Mandatory
class Initiative(object):
    pass


class Programme(Initiative):
    pass


class Project(Initiative):
    pass


class SubProject(Initiative):
    pass


class WorkPackage(Initiative):
    pass


class Task(Initiative):
    pass


class InitiativeLifeCyclePhase(object):
    pass


class LifeCyclePhase(object):
    pass




