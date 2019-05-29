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
        'nvr': 'body.build.nvr',
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
    },
    'GreenwaveDecisionUpdate': {
        'matches': ['/topic/VirtualTopic.eng.greenwave.decision.update'],
        'topic': 'topic',
        'msg_id': 'headers.message-id',
        'decision_context': 'body.msg.decision_context',
        'subject_identifier': 'body.msg.subject_identifier',
        'policies_satisfied': 'body.msg.policies_satisfied'
    }
}

services = ['brew', 'mbs', 'greenwave']
topic_suffix = '.>'
dest_prefix = '/topic/VirtualTopic.eng.mbs'
