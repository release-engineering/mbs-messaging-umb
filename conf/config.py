message_mapping = {
    'KojiBuildChange': {
        'matches': [
            '/topic/VirtualTopic.eng.brew.build.building',
            '/topic/VirtualTopic.eng.brew.build.complete',
            '/topic/VirtualTopic.eng.brew.build.deleted',
            '/topic/VirtualTopic.eng.brew.build.failed',
            '/topic/VirtualTopic.eng.brew.build.canceled',
        ],
        'topic': 'topic',
        'msg_id': 'headers.message-id',
        'build_id': 'body.info.id',
        'task_id': 'body.info.task_id',
        'build_new_state': 'body.new',
        'build_name': 'body.info.name',
        'build_version': 'body.info.version',
        'build_release': 'body.info.release',
    },
    'KojiTagChange': {
        'matches': ['/topic/VirtualTopic.eng.brew.build.tag'],
        'topic': 'topic',
        'msg_id': 'headers.message-id',
        'tag': 'body.tag.name',
        'artifact': 'body.build.name',
        'build_id': 'body.build.build_id',
    },
    'KojiRepoChange': {
        'matches': ['/topic/VirtualTopic.eng.brew.repo.done'],
        'topic': 'topic',
        'msg_id': 'headers.message-id',
        'repo_tag': 'body.repo.tag_name',
    },
    'MBSModule': {
        'matches': ['/topic/VirtualTopic.eng.mbs.module.state.change'],
        'topic': 'topic',
        'msg_id': 'headers.message-id',
        'module_build_id': 'body.id',
        'module_build_state': 'body.state',
    }
}

services = ['brew', 'mbs']
topic_suffix = '.>'
dest_prefix = '/topic/VirtualTopic.eng.mbs'
