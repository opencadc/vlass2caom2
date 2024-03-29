# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2020.                            (c) 2020.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
# ***********************************************************************
#

from datetime import datetime
from os import chdir, getcwd
from os.path import dirname, join, realpath
from treelib import Tree

from caom2pipe import html_data_source
from caom2pipe.manage_composable import Config, ExecutionReporter, make_datetime, Observable, State, write_as_yaml
from vlass2caom2 import data_source
from vlass2caom2 import storage_name

from mock import Mock, patch

THIS_DIR = dirname(realpath(__file__))
TEST_DATA_DIR = join(THIS_DIR, 'data')
TEST_START_TIME_STR = '24Apr2019 12:34'
ALL_FIELDS = join(TEST_DATA_DIR, 'all_fields_list.html')
CROSS_EPOCH = join(TEST_DATA_DIR, 'cross_epoch.html')
PIPELINE_INDEX = join(TEST_DATA_DIR, 'pipeline_weblog_quicklook.htm')
QL_INDEX = join(TEST_DATA_DIR, 'vlass_quicklook.html')
REJECT_INDEX = join(TEST_DATA_DIR, 'rejected_index.html')
SE_OBS_ID_PAGE = join(TEST_DATA_DIR, 'se_obs_id_page.html')
SE_SINGLE_PAGE = join(TEST_DATA_DIR, 'se_single_page.html')
SE_TILE_PAGE = join(TEST_DATA_DIR, 'se_tile_page.html')
SINGLE_FIELD_DETAIL = join(TEST_DATA_DIR, 'single_field_detail.html')
SINGLE_TILE = join(TEST_DATA_DIR, 'single_tile_list.html')
SPECIFIC_NO_FILES = join(TEST_DATA_DIR, 'no_files.html')
SPECIFIC_REJECTED = join(TEST_DATA_DIR, 'specific_rejected.html')
SE_TOP_PAGE = join(TEST_DATA_DIR, 'se_top_page.html')


class TestFilterFunctions:
    # test filter functions in the DataSource specializations

    def _ini(self, test_config, tmp_path, test_url, test_filter):
        self._test_config = test_config
        self._test_config.change_working_directory(tmp_path)
        self._test_config.data_sources = [storage_name.QL_URL]
        self._test_config.data_source_extensions = ['.fits', '.csv']
        self._session_mock = Mock()
        test_start_key = storage_name.QL_URL
        State.write_bookmark(test_config.state_fqn, test_start_key, make_datetime(TEST_START_TIME_STR))
        self._test_templates = data_source.VlassHtmlTemplate(test_config)
        self._test_subject = data_source.VlassPages(
            test_config, test_start_key, self._test_templates, self._session_mock
        )
        assert self._test_subject is not None, 'ctor failure'
        self._test_subject.initialize_start_dt()
        self._test_tree = Tree()
        self._test_tree.create_node(tag=test_url, identifier=test_url, data=test_filter)
        self._test_node = self._test_tree.get_node(test_url)

    def test_single_tile(self, test_config, tmp_path):
        test_url = f'{storage_name.QL_URL}T07t13/'
        self._ini(test_config, tmp_path, test_url, html_data_source.HtmlFilter(data_source.filter_by_epoch_name, False))
        with open(SINGLE_TILE) as f:
            test_content = f.read()
            test_result = self._test_subject._parse_html_string(self._test_node, test_content)
            assert test_result is not None, 'expected a result'
            assert len(test_result) == 1, 'wrong number of results'
            first_answer = next(iter(sorted(test_result.items())))
            assert len(first_answer) == 2, 'wrong number of results'
            assert first_answer[0] == f'{test_url}VLASS1.2.ql.T07t13.J083838-153000.10.2048.v1/'
            assert first_answer[1] == datetime(2019, 4, 28, 15, 18)

    def test_reject_index(self, test_config, tmp_path):
        test_url = 'https://localhost:8080/VLASS1.2/QA_REJECTED/'
        self._ini(test_config, tmp_path, test_url, html_data_source.HtmlFilter(data_source.filter_by_epoch_name, False))
        with open(REJECT_INDEX) as f:
            test_content = f.read()
            test_result = self._test_subject._parse_html_string(self._test_node, test_content)
            assert test_result is not None, 'expect a result'
            assert len(test_result) == 1, 'wrong number of results'
            first_answer = next(iter(sorted(test_result.items())))
            assert len(first_answer) == 2, 'wrong number of results'
            assert (
                first_answer[0]
                == f'{test_url}VLASS1.2.ql.T21t15.J141833+413000.10.2048.v1/'
            ), f'{first_answer[0]}'
            assert first_answer[1] == datetime(2019, 5, 1, 10, 30), 'wrong date result'

    def test_all_tiles(self, test_config, tmp_path):
        test_url = storage_name.QL_URL
        self._ini(test_config, tmp_path, test_url, html_data_source.HtmlFilter(data_source.filter_by_tile, True))
        with open(ALL_FIELDS) as f:
            test_content = f.read()
            test_result = self._test_subject._parse_html_string(self._test_node, test_content)
            assert test_result is not None, 'expected a result'
            assert len(test_result) == 2, 'wrong number of results'
            first_answer = next(iter(test_result.items()))
            assert len(first_answer) == 2, 'wrong number of results'
            assert first_answer[0] == f'{test_url}T07t13/', 'wrong content'
            assert first_answer[1] == datetime(2019, 4, 29, 8, 2)

    def test_se_top_page(self, test_config, tmp_path):
        test_url = 'https://localhost:8080/'
        self._ini(test_config, tmp_path, test_url, html_data_source.HtmlFilter(data_source.filter_by_epoch, True))
        with open(SE_TOP_PAGE) as f:
            test_content = f.read()
            test_result = self._test_subject._parse_html_string(self._test_node, test_content)
            assert test_result is not None, 'expect a top page result'
            assert len(test_result) == 1, 'wrong top page length'
            first_answer = next(iter(sorted(test_result.items())))
            assert len(first_answer) == 2, 'wrong number of results'
            assert first_answer[0] == f'{test_url}VLASS2.1/', 'wrong top page url'
            assert first_answer[1] == datetime(2022, 7, 26, 16, 31), 'wrong top page datetime'

    def test_se_single_page(self, test_config, tmp_path):
        test_url = 'https://localhost:8080/VLASS1.2/T21t15/VLASS1.2.se.T21t15.J141833+413000.10.2048.v1/'
        test_config.data_source_extensions = ['.fits', '.csv']
        template = html_data_source.HtmlFilteredPagesTemplate(test_config)
        self._ini(test_config, tmp_path, test_url, template._file_filter)
        with open(SE_SINGLE_PAGE) as f:
            test_content = f.read()
            test_result = self._test_subject._parse_html_string(self._test_node, test_content)
            assert test_result is not None, 'expect a specific page result'
            assert len(test_result) == 7, 'wrong specific page length'
            first_answer = next(iter(sorted(test_result.items())))
            assert len(first_answer) == 2, 'wrong number of results'
            assert (
                first_answer[0] == f'{test_url}VLASS2.1.se.T10t01.J000200-003000.06.2048.v1.I.catalog.csv'
            ), 'wrong top page url'
            assert first_answer[1] == datetime(2022, 5, 16, 16, 24), 'wrong top page datetime'


def test_metadata_scrape():
    test_state = Mock()
    mock_session = Mock()
    test_subject = data_source.WebLogMetadata(test_state, mock_session, [storage_name.QL_URL])
    assert test_subject is not None, 'ctor failure'

    with open(SINGLE_FIELD_DETAIL) as f:
        test_content = f.read()
        test_result = test_subject._parse_single_field(test_content)
        assert test_result is not None, 'expected a result'
        assert len(test_result) == 4, 'wrong number of fields'
        assert (
            test_result['Pipeline Version'] == '42270 (Pipeline-CASA54-P2-B)'
        ), 'wrong pipeline'
        assert (
            test_result['Observation Start'] == '2019-04-12 00:10:01'
        ), 'wrong start'
        assert (
            test_result['Observation End'] == '2019-04-12 00:39:18'
        ), 'wrong end'
        assert test_result['On Source'] == '0:03:54', 'wrong tos'


@patch('caom2pipe.html_data_source.query_endpoint_session')
def test_quicklook(query_endpoint_mock, test_config, tmp_path):
    query_endpoint_mock.side_effect = _query_quicklook_endpoint
    test_config.change_working_directory(tmp_path)
    test_start_key = storage_name.QL_URL
    test_config.data_sources = [test_start_key]
    test_start_time = datetime(2019, 4, 22)
    State.write_bookmark(test_config.state_fqn, test_start_key, test_start_time)
    session_mock = Mock()

    orig_getcwd = getcwd()
    try:
        chdir(tmp_path)
        Config.write_to_file(test_config)
        test_templates = data_source.VlassHtmlTemplate(test_config)
        test_subject = data_source.VlassPages(test_config, storage_name.QL_URL, test_templates, session_mock)
        assert test_subject is not None, 'ctor failure'
        test_reporter = ExecutionReporter(test_config, Observable(test_config))
        test_subject.reporter = test_reporter
        test_subject.initialize_start_dt()
        test_subject.initialize_end_dt()
        assert test_subject.end_dt is not None, 'expected date result'
        assert test_subject.end_dt == datetime(2020, 4, 16, 16, 43), 'wrong date result'
        assert len(test_subject._work) == 2, 'wrong amount of work'
        time_box_end_time = datetime(2020, 4, 16, 15, 45)
        test_result = test_subject.get_time_box_work(test_start_time, time_box_end_time)
        assert test_result is not None, 'expected dict result'
        assert len(test_result) == 1, 'wrong size results'
        temp = sorted([ii.entry_name for ii in test_result])
        assert (
            temp[0]
            == 'https://archive-new.nrao.edu/vlass/quicklook/VLASS1.1/T01t01/'
               'VLASS1.1.ql.T01t01.J000228-363000.10.2048.v1/'
               'VLASS1.1.ql.T01t01.J000228-363000.10.2048.v1.I.iter1.image.pbcor.tt0.rms.subim.fits'
        ), 'wrong result'
        assert test_reporter._summary._entries_sum == 1, f'wrong entries {test_reporter._summary.report()}'
    finally:
        chdir(orig_getcwd)


@patch('caom2pipe.html_data_source.query_endpoint_session')
def test_continuum(query_endpoint_mock, test_config, tmp_path):
    query_endpoint_mock.side_effect = _query_continuum_endpoint
    test_config.change_working_directory(tmp_path)
    test_config.data_sources = [storage_name.SE_URL]
    test_start_time = datetime(2022, 5, 15, 0, 0, 0)
    session_mock = Mock()

    orig_getcwd = getcwd()
    try:
        chdir(tmp_path)
        Config.write_to_file(test_config)
        State.write_bookmark(test_config.state_fqn, storage_name.SE_URL, test_start_time)

        test_templates = data_source.VlassHtmlTemplate(test_config)
        test_subject = data_source.VlassPages(test_config, storage_name.SE_URL, test_templates, session_mock)
        assert test_subject is not None, 'ctor failure'
        test_reporter = ExecutionReporter(test_config, Observable(test_config))
        test_subject.reporter = test_reporter
        test_subject.initialize_start_dt()
        test_subject.initialize_end_dt()

        assert test_subject.end_dt is not None, 'expected date result'
        assert test_subject.end_dt == datetime(2022, 5, 16, 16, 24), 'wrong date result'
        # 36 == the same 6 files returned for each of 3 observations * 2 tiles
        assert len(test_subject._work) == 36, 'wrong amount of work'

        time_box_end_time = datetime(2022, 5, 16, 16, 24)
        test_result = test_subject.get_time_box_work(test_start_time, time_box_end_time)
        assert test_result is not None, 'expected dict result'
        assert len(test_result) == 36, 'wrong size results'
        temp = sorted([ii.entry_name for ii in test_result])
        assert (
            temp[0]
            == 'https://archive-new.nrao.edu/vlass/se_continuum_imaging/VLASS2.1/T10t01/'
               'VLASS2.1.se.T10t01.J000200-003000.06.2048.v1/'
               'VLASS2.1.se.T10t01.J000200-003000.06.2048.v1.I.iter3.alpha.error.subim.fits'
        ), f'wrong result {temp[0]}'
        assert test_reporter._summary._entries_sum == 36, f'wrong entries {test_reporter._summary.report()}'
    finally:
        chdir(orig_getcwd)


def _close():
    pass


def _query_quicklook_endpoint(url, session, timeout=-1):
    result = type('response', (), {})
    result.text = None
    result.close = _close
    # just need a reference that causes no action
    result.raise_for_status = _close

    if (
        url == 'https://archive-new.nrao.edu/vlass/quicklook/VLASS1.2v2/'
               'T07t13/VLASS1.2.ql.T07t13.J080203-133000.10.2048.v1/'
    ):
        with open(f'{TEST_DATA_DIR}/file_list.html', 'r') as f:
            result.text = f.read()
    elif (
        url.startswith('https://archive-new.nrao.edu/vlass/quicklook/VLASS')
        and url.endswith('.10.2048.v1/')
        and 'QA_REJECTED' not in url
    ):
        with open(SPECIFIC_NO_FILES) as f:
            result.text = f.read()
    elif url.endswith('index.html'):
        with open(SINGLE_FIELD_DETAIL) as f:
            result.text = f.read()
    elif url == storage_name.QL_URL:
        with open(QL_INDEX) as f:
            result.text = f.read()
    elif 'vlass/quicklook/VLASS1.2v2/QA_REJECTED/VLASS1.2.ql' in url:
        with open(SPECIFIC_REJECTED) as f:
            result.text = f.read()
    elif 'QA_REJECTED' in url:
        with open(REJECT_INDEX) as f:
            result.text = f.read()
    elif len(url.split('/')) == 8:
        if 'weblog' in url:
            with open(PIPELINE_INDEX) as f:
                result.text = f.read()
        else:
            if 'VLASS1.1' in url:
                result.text = ''
            else:
                with open(SINGLE_TILE) as f:
                    result.text = f.read()
    elif (
        url.endswith('VLASS1.1/')
        or url.endswith('VLASS2.1/')
        or url.endswith('VLASS2.2/')
        or url.endswith('VLASS1.2v2/')
        or url.endswith('VLASS1.2/')
    ):
        with open(ALL_FIELDS) as f:
            result.text = f.read()
    else:
        raise Exception(f'wut? {url}')
    return result


def _query_continuum_endpoint(url, session, timeout=-1):
    result = type('response', (), {})
    result.text = None
    result.close = _close
    # just need a reference that causes no action
    result.raise_for_status = _close

    # https://archive-new.nrao.edu/vlass/se_continuum_imaging/VLASS2.1/T10t01/
    # VLASS2.1.se.T10t01.J000200-013000.06.2048.v1/
    if (
        url.startswith('https://archive-new.nrao.edu/vlass/se_continuum_imaging/VLASS2.1/T')
        and url.endswith('.06.2048.v1/')
    ):
        with open(SE_SINGLE_PAGE) as f:
            result.text = f.read()
    elif url == 'https://archive-new.nrao.edu/vlass/se_continuum_imaging/VLASS2.1/':
        with open(SE_TILE_PAGE) as f:
            result.text = f.read()
    elif url == storage_name.SE_URL:
        with open(SE_TOP_PAGE) as f:
            result.text = f.read()
    elif url.startswith('https://archive-new.nrao.edu/vlass/se_continuum_imaging/VLASS2.1/T'):
        with open(SE_OBS_ID_PAGE) as f:
            result.text = f.read()
    else:
        raise Exception(f'wut? {url}')
    return result


def _write_state(start_time_str, f_name, test_config):
    test_time = make_datetime(start_time_str)
    test_bookmark = {'bookmarks': {}}
    for ds in test_config.data_sources:
        test_bookmark['bookmarks'][ds] = {'last_record': test_time}
    test_bookmark['context'] = {
            'vlass_context': {
                'VLASS1.1': '01-Jan-2018 00:00',
                'VLASS1.2v2': '01-Nov-2018 00:00',
                'VLASS2.1': '01-Jul-2020 00:00',
                'VLASS2.2': '01-Jul-2021 00:00',
            },
        }
    write_as_yaml(test_bookmark, f_name)
