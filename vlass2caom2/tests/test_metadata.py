# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2021.                            (c) 2021.
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
#  : 4 $
#
# ***********************************************************************
#

from mock import patch

from datetime import datetime
from vlass2caom2 import metadata

import test_scrape


@patch('caom2pipe.manage_composable.query_endpoint')
def test_cache(query_endpoint_mock):
    query_endpoint_mock.side_effect = test_scrape._query_endpoint

    # preconditions
    # because 'cache' is globally declared in metadata.py, this test requires
    # a config.yml file in the test working directory, just based on the
    # import statement
    test_subject = metadata.cache
    assert test_subject is not None, 'expect a test subject'
    test_subject._refresh_bookmark = 'None'
    test_subject._qa_rejected_obs_ids = []
    try:
        test_obs_id = 'VLASS1.2.T21t15.J141833+413000'
        test_result = test_subject.is_qa_rejected(test_obs_id)
        assert test_result is True, 'expected qa rejected obs id'
        assert type(test_subject._refresh_bookmark) is datetime, \
            f'post-condition 1 {test_subject._refresh_bookmark}'
        assert len(test_subject._qa_rejected_obs_ids) == 4, 'post-condition 2'

        test_obs_id = 'VLASS1.1.T03t13.J080215-283000'
        test_result = test_subject.is_qa_rejected(test_obs_id)
        assert test_result is False, 'expected obs id to not be qa rejected'
        assert len(test_subject._qa_rejected_obs_ids) == 4, 'post-condition 2'

    finally:
        # cleanup
        test_subject.add_to(metadata.REFRESH_BOOKMARK, 'None')
        test_subject.add_to(metadata.QA_REJECTED_OBS_IDS, None)
        test_subject.save()