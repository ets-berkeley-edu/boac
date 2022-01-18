/**
 * Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

-- Temporary SQL script for BOAC-845. Please refer there for more information.

-- This script must be run from inside the psql client:
--
-- Usage:
--
--     psql -U DBUSER postgresql://SOMEPLACE.amazonaws.com:SOMEPORT/BOACDB
--     BOACDB=>  \i scripts/db/tools/copy_external_cache_from_file
--
-- The input file should be named 'external_json_cache.bin'.

\timing on
BEGIN;
LOCK TABLE json_cache;
DELETE FROM json_cache WHERE key NOT LIKE 'job_%' AND key NOT LIKE 'asc_athletes_%';
\COPY json_cache (created_at, updated_at, key, json) from 'external_json_cache.bin' WITH (FORMAT BINARY)
COMMIT;
VACUUM ANALYZE json_cache;
\timing off
