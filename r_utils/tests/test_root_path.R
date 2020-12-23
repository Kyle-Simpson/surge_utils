#----# INFO #----# ####
# Script : test_root_path.R
# Description: Automated testing of Root & Path functions
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

#----# Test Get Core Ref #----# ####
test_that('Test Get Core Ref', {
  expect_error(get_core_ref(param_name = NULL))
  
  gbd_rid <- yaml.load_file(paste0(code_repo, "refs.yaml"))$gbd_round_id
  expect_equal(gbd_rid, get_core_ref('gbd_round_id'))
})
#-----------------------------# ####

#----# Test Get Root #----# ####
test_that('Test Get Root', {
  h <- paste0('/ihme/homes/', Sys.info()['user'][1], '/')
  expect_equal(h, .get_root('h'))
})
#-------------------------# ####

#----# Test Set Roots #----# ####
test_that('Test Set Roots', {
  h <- paste0('/ihme/homes/', Sys.info()['user'][1], '/')
  expect_equal(h, .set_roots()$h)
})
#--------------------------# ####

rm(list=ls())