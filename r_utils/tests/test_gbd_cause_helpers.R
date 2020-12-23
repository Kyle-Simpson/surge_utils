#----# INFO #----# ####
# Script : test_gbd_cause_helpers.R
# Description: Automated testing of GBD Cause functions
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

#----# Test Add Cause ID #----# ####
test_that('Add Cause ID', {
  # Bad expected cols
  expect_error(add_cause_id(data.table()))
  
  # Perf cause_id
  expect_equal(add_cause_id(data.table('cause_name' = c( 'All causes'), 'cause_id' = c(294))), 
               data.table('cause_name' = c( 'All causes'), 'cause_id' = c(294)))
  
  # Proper use by acause
  df <- data.table('acause' = c('_all'))
  expect_equal(add_cause_id(df)$cause_id, 294)
  
  # Proper use by cause_name
  df <- data.table('cause_name' = c('All causes'))
  expect_equal(add_cause_id(df)$cause_id, 294)
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_cause_id(df))), 2)
})
#-----------------------------# ####

#----# Test Add Acause #----# ####
test_that('Add Acause', {
  # Bad expected cols
  expect_error(add_acause(data.table()))
  
  # Perf acause
  expect_equal(add_acause(data.table('cause_name' = c('All causes'), 'acause' = c('_all'))),
               data.table('cause_name' = c('All causes'), 'acause' = c('_all')))
  
  # Proper use by cause_id
  df <- data.table('cause_id' = c(294))
  expect_equal(add_acause(df)$acause, '_all')
  
  # Proper use by cause_name
  df <- data.table('cause_name' = c('All causes'))
  expect_equal(add_acause(df)$acause, '_all')
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_acause(df))), 2)
})
#---------------------------# ####

#----# Test Add Cause Name #----# ####
test_that('Add Cause Name', {
  # Bad expected cols
  expect_error(add_cause_name(data.table()))
  
  # Perf cause_id
  expect_equal(add_cause_name(data.table('cause_name' = c('All causes'), 'acause' = c('_all'))),
               data.table('cause_name' = c('All causes'), 'acause' = c('_all')))
  
  # Proper use by cause_id
  df <- data.table('cause_id' = c(294))
  expect_equal(add_cause_name(df)$cause_name, 'All causes')
  
  # Proper use by acause
  df <- data.table('acause' = c('_all'))
  expect_equal(add_cause_name(df)$cause_name, 'All causes')
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_cause_name(df))), 2)
})
#-------------------------------# ####

#----# Test Add Cause Lancet Label #----# ####
test_that('Add Cause Lancet Label', {
  # Bad expected cols
  expect_error(add_cause_lancet_label(data.table()))
  
  # Perf cause_id
  expect_equal(add_cause_lancet_label(data.table('cause_name' = c('All causes'), 'lancet_label' = c('All Causes'))),
               data.table('cause_name' = c('All causes'), 'lancet_label' = c('All Causes')))
  
  # Proper use by cause_id
  df <- data.table('cause_id' = c(294))
  expect_equal(add_cause_lancet_label(df)$lancet_label, 'All causes')
  
  # Proper use by acause
  df <- data.table('acause' = c('_all'))
  expect_equal(add_cause_lancet_label(df)$lancet_label, 'All causes')
  
  # Proper use by cause_name
  df <- data.table('cause_name' = c('All causes'))
  expect_equal(add_cause_lancet_label(df)$lancet_label, 'All causes')
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_cause_lancet_label(df))), 2)
})
#---------------------------------------# ####

rm(list=ls())