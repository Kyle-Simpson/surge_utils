#----# INFO #----# ####
# Script : run_all_tests.R
# Description: Automated testing of all functions
# Contributors: Kyle Simpson
#----------------# ####

#----# Environment Prep #----# ####
rm(list=ls())

if (!exists("code_repo"))  {
  code_repo <- unname(ifelse(Sys.info()['sysname'] == "Windows", "H:/repos/surge_utils/", paste0("/ihme/homes/", Sys.info()['user'][1], "/repos/surge_utils/")))
}
pacman::p_load(testthat)
#----------------------------# ####

#----# Test everything #----# ####
testthat::test_dir(paste0(code_repo, 'r_utils/tests/'))
#---------------------------# ####

rm(list=ls())