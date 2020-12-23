#----# INFO #----# ####
# Script : test_qsub_helpers.R
# Description: Automated testing of QSUB Helpers
# Contributors: Kyle Simpson
#----------------# ####

#----# Environment Prep #----# ####
rm(list=ls())

if (!exists("code_repo"))  {
  code_repo <- unname(ifelse(Sys.info()['sysname'] == "Windows", "H:/repos/surge_utils/", paste0("/ihme/homes/", Sys.info()['user'][1], "/repos/surge_utils/")))
}
source(paste0(code_repo, 'r_utils/utils.R'))
pacman::p_load(testthat)
#----------------------------# ####

#----# Test Launch QSUB #----# ####
test_that('Launch QSUB', {
  # Bad errors_path
  expect_error(launch_qsub(errors_path = '', output_path = '/ihme/homes/', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  
  # Bad output_path
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  
  # Bad job_name
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = NULL, 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = '', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  
  # Bad queue
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='t.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  
  # Bad cluster_project
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = '', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  
  # Bad num_threads
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = NULL, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = '1', 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  
  # Bad num_gigs
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = NULL, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = '1', runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r'))
  
  # Bad runtime
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = NULL, script_path = '/ihme/', 
                           script_language = 'r'))
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = 1, script_path = '/ihme/', 
                           script_language = 'r'))
  
  # Bad script_path
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = NULL, 
                           script_language = 'r'))
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = 1, 
                           script_language = 'r'))
  
  # Bad script_language
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = NULL))
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'bad'))
  
  # Bad extra_args
  expect_error(launch_qsub(errors_path = '/ihme/homes/', output_path = '/ihme/homes.', job_name = 'test', 
                           queue='i.q', cluster_project = 'ihme_general', num_threads = 1, 
                           num_gigs = 1, runtime = '00:01:00', script_path = '/ihme/', 
                           script_language = 'r', extra_args = 1))
  
  # Proper use
  succeed(launch_qsub(job_name = 'test',
                      queue='i.q', cluster_project = 'ihme_general', num_threads = 1,
                      num_gigs = 1, runtime = '00:01:00', script_path = paste0(code_repo, 'r_utils/tests/test_root_path.R'),
                      script_language = 'r'))
  succeed(launch_qsub(job_name = 'test',
                      queue='i.q', cluster_project = 'ihme_general', num_threads = 1,
                      num_gigs = 1, runtime = '00:01:00', script_path = paste0(code_repo, 'py_utils/tests/test_root_path.py'),
                      script_language = 'python'))
  
})
#----------------------------# ####

rm(list=ls())