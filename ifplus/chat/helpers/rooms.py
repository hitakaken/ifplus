# -*- coding: utf-8 -*-
from abc import ABCMeta


class ChatRooms(object):
    __metaclass__ = ABCMeta

    def find_one_by_id(self, rid):
        return None

# findOneByIdOrName

# findOneByImportId

# findOneByName

# findOneByNameAndType

# findOneByIdContainigUsername

# findOneByNameAndTypeNotContainigUsername

# findById

# findByIds

# findByType

# findByTypes

# findByUserId

# findByNameContaining

# findByNameContainingTypesWithUsername

# findContainingTypesWithUsername

# findByNameContainingAndTypes

# findByNameAndTypeNotContainingUsername

# findByNameStartingAndTypes

# findByDefaultAndTypes

# findByTypeContainigUsername

# findByTypeContainigUsernames

# findByTypesAndNotUserIdContainingUsername

# findByContainigUsername

# findByTypeAndName

# findByTypeAndNameContainingUsername

# findByTypeAndArchivationState

# archiveById

# unarchiveById

# addUsernameById

# addUsernamesById

# addUsernameByName

# removeUsernameById

# removeUsernamesById

# removeUsernameFromAll

# removeUsernameByName

# setNameById

# incMsgCountAndSetLastMessageTimestampById

# replaceUsername

# replaceMutedUsername

# replaceUsernameOfUserByUserId

# setJoinCodeById

# setUserById

# setTypeById

# setTopicById

# muteUsernameByRoomId

# unmuteUsernameByRoomId

# saveDefaultById

# saveRoomById

# createWithTypeNameUserAndUsernames

# createWithIdTypeAndName

# removeById

# removeByTypeContainingUsername

