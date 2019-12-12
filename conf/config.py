message_mapping = {
    'koji_build_change': {
        'matches': [
            '/topic/VirtualTopic.eng.brew.build.building',
            '/topic/VirtualTopic.eng.brew.build.complete',
            '/topic/VirtualTopic.eng.brew.build.deleted',
            '/topic/VirtualTopic.eng.brew.build.failed',
            '/topic/VirtualTopic.eng.brew.build.canceled',
        ],
        'topic': 'topic',
        'msg_id': 'headers.message-id',
        'task_id': 'body.info.task_id',
        'build_new_state': 'body.new',
        'build_name': 'body.info.name',
        'build_version': 'body.info.version',
        'build_release': 'body.info.release',
        'module_build_id': None,
        'state_reason': None,
    },
    'koji_tag_change': {
        'matches': ['/topic/VirtualTopic.eng.brew.build.tag'],
        'topic': 'topic',
        'msg_id': 'headers.message-id',
        'tag_name': 'body.tag.name',
        'build_nvr': 'body.build.nvr',
    },
    'koji_repo_change': {
        'matches': ['/topic/VirtualTopic.eng.brew.repo.done'],
        'topic': 'topic',
        'msg_id': 'headers.message-id',
        'tag_name': 'body.repo.tag_name',
    },
    'mbs_module_state_change': {
        'matches': ['/topic/VirtualTopic.eng.mbs.module.state.change'],
        'topic': 'topic',
        'msg_id': 'headers.message-id',
        'module_build_id': 'body.id',
        'module_build_state': 'body.state',
    },
    'greenwave_decision_update': {
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
