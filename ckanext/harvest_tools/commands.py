from ckan.lib.cli import CkanCommand
# No other CKAN imports allowed until _load_config is run,
# or logging is disabled


class Clean(CkanCommand):
    """
    Cleans the `harvest_object` and `harvest_object_error` tables
    """
    summary = __doc__.split('\n')[0]

    def __init__(self, name):

        super(Clean, self).__init__(name)

    def command(self):
        self._load_config()

        import ckan.plugins.toolkit as toolkit

        log = __import__('logging').getLogger(__name__)

        try:
            toolkit.get_action('clean_harvest_object_table')(None, {})
            log.info('Completed `clean_harvest_object_table`')
        except Exception, e:
            log.error('Error running `clean_harvest_object_table`')
            log.error(str(e))

        return


class CheckHarvestObjects(CkanCommand):
    """
    Sends an email alert if the `harvest_object` table size exceeds certain thresholds
    """
    summary = __doc__.split('\n')[0]

    def __init__(self, name):

        super(CheckHarvestObjects, self).__init__(name)

    def command(self):
        self._load_config()

        import ckan.plugins.toolkit as toolkit
        from ckan.common import config
        from ckanext.harvest_tools import helpers

        log = __import__('logging').getLogger(__name__)

        try:
            report = toolkit.get_action('harvest_object_report')(None, {})

            if 'alerts' in report and len(report['alerts']) > 0:
                helpers.send_notification_email(
                    template='notification-harvest-object-table',
                    extra_vars={
                        "alerts": report['alerts'],
                        "url": config.get('ckan.site_url') + '/harvest/table_report'
                    }
                )
        except Exception, e:
            log.error('Error calling `harvest_object_report`')
            log.error(str(e))

        return


class LongRunning(CkanCommand):
    """
    Sends an email alert if any long running harvest jobs are identified
    """
    summary = __doc__.split('\n')[0]

    def __init__(self, name):

        super(LongRunning, self).__init__(name)

    def command(self):
        self._load_config()

        import ckan.plugins.toolkit as toolkit

        from ckan.common import config
        from ckanext.harvest_tools import helpers

        log = __import__('logging').getLogger(__name__)

        urls = []

        try:
            report = toolkit.get_action('long_running_harvest_jobs')(None, {})

            for job in report['job_details']:
                urls.append(config.get('ckan.site_url') + '/harvest/' + job['source_id'] + '/job/' + job['id'])

            if report['alerts']:
                helpers.send_notification_email(
                    template='notification-long-running-job',
                    extra_vars={
                        "alerts": report['alerts'],
                        "urls": urls
                    }
                )
        except Exception, e:
            log.error('Error calling `long_running_harvest_jobs`')
            log.error(str(e))

        return
