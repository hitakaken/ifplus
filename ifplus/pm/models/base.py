# -*- coding: utf-8 -*-


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
    def __init__(self, underlying, pm=None):
        self.underlying = underlying
        self.pm = pm

    @property
    def name(self):
        return self.underlying[u'name']
