#----# INFO #----# ####
# Script : test_gbd_loc_helpers.R
# Description: Automated testing of GBD Location helpers
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

#----# Test Add IHME Loc ID #----# ####
test_that('Add IHME Loc ID', {
  # Bad expected cols
  expect_error(add_ihme_loc_id(data.table()))
  
  # Perf ihme_loc_id
  expect_equal(add_ihme_loc_id(data.table('location_id' = c(1), 'ihme_loc_id' = c('G'))), 
               data.table('location_id' = c(1), 'ihme_loc_id' = c('G')))
  
  # Proper use by location_id
  df <- data.table('location_id' = c(1))
  expect_equal(add_ihme_loc_id(df)$ihme_loc_id, 'G')
  
  # Proper use by location_name
  df <- data.table('location_name' = c('Global'))
  expect_equal(add_ihme_loc_id(df)$ihme_loc_id, 'G')
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_ihme_loc_id(df))), 2)
})
#--------------------------------# ####

#----# Test Add Location Name #----# ####
test_that('Add Location Name', {
  # Bad expected cols
  expect_error(add_location_name(data.table()))
  
  # Perf location_name
  expect_equal(add_location_name(data.table('location_id' = c(1), 'location_name' = c('Global'))),
               data.table('location_id' = c(1), 'location_name' = c('Global')))
  
  # Proper use with ihme_loc_id
  df <- data.table('ihme_loc_id' = c('G'))
  expect_equal(add_location_name(df)$location_name, 'Global')
  
  # Proper use with location_id
  df <- data.table('location_id' = c(1))
  expect_equal(add_location_name(df)$location_name, 'Global')
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_location_name(df))), 2)
})
#----------------------------------# ####

#----# Test Add Region ID #----# ####
test_that('Add Region ID', {
  # Bad expected cols
  expect_error(add_region_id(data.table()))
  
  # Perf region_id
  expect_equal(add_region_id(data.table('ihme_loc_id' = c('R2'), 'region_id' = c(32))),
               data.table('ihme_loc_id' = c('R2'), 'region_id' = c(32)))
  
  # Proper use ihme_loc_id
  df <- data.table('ihme_loc_id' = c('R2'))
  expect_equal(add_region_id(df)$region_id, 32)
  
  # Proper use location_id
  df <- data.table('location_id' = c(32))
  expect_equal(add_region_id(df)$region_id, 32)
  
  # Proper use location_name
  df <- data.table('location_name' = c('Central Asia'))
  expect_equal(add_region_id(df)$region_id, 32)
  
  # Proper use region_name
  df <- data.table('region_name' = c('Central Asia'))
  expect_equal(add_region_id(df)$region_id, 32)
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_region_id(df))), 2)
})
#------------------------------# ####

#----# Test Add Region Name #----# ####
test_that('Add Region Name', {
  # Bad expected cols
  expect_error(add_region_name(data.table()))
  
  # Perf region_name
  expect_equal(add_region_name(data.table('ihme_loc_id' = c('R2'), 'region_name' = c('Central Asia'))),
               data.table('ihme_loc_id' = c('R2'), 'region_name' = c('Central Asia')))
  
  # Proper use by ihme_loc_id
  df <- data.table('ihme_loc_id' = c('R2'))
  expect_equal(add_region_name(df)$region_name, 'Central Asia')
  
  # Proper use by location_id
  df <- data.table('location_id' = c(32))
  expect_equal(add_region_name(df)$region_name, 'Central Asia')
  
  # Proper use by location_name
  df <- data.table('location_name' = c('Central Asia'))
  expect_equal(add_region_name(df)$region_name, 'Central Asia')
  
  # Proper use by region_id
  df <- data.table('region_id' = c(32))
  expect_equal(add_region_name(df)$region_name, 'Central Asia')
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_region_name(df))), 2)
})
#--------------------------------# ####

#----# Test Add Super Region ID #----# ####
test_that('Add Super Region ID', {
  # Bad expected cols
  expect_error(add_super_region_id(data.table()))
  
  # Perf region_name
  expect_equal(add_super_region_id(data.table('ihme_loc_id' = c('R2'), 'super_region_id' = c(31))),
               data.table('ihme_loc_id' = c('R2'), 'super_region_id' = c(31)))
  
  # Proper use by ihme_loc_id
  df <- data.table('ihme_loc_id' = c('R2'))
  expect_equal(add_super_region_id(df)$super_region_id, 31)
  
  # Proper use by location_id
  df <- data.table('location_id' = c(32))
  expect_equal(add_super_region_id(df)$super_region_id, 31)
  
  # Proper use by location_name
  df <- data.table('location_name' = c('Central Asia'))
  expect_equal(add_super_region_id(df)$super_region_id, 31)
  
  # Proper use by region_id
  df <- data.table('region_id' = c(32))
  expect_equal(add_super_region_id(df)$super_region_id, 31)
  
  # Proper use by region_name
  df <- data.table('region_name' = c('Central Asia'))
  expect_equal(add_super_region_id(df)$super_region_id, 31)
  
  # Proper use by super_region_name
  df <- data.table('super_region_name' = c('Central Europe, Eastern Europe, and Central Asia'))
  expect_equal(add_super_region_id(df)$super_region_id, 31)
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_super_region_id(df))), 2)
})
#------------------------------------# ####

#----# Test Add Super Region Name #----# ####
test_that('Add Super Region Name', {
  # Bad expected cols
  expect_error(add_super_region_name(data.table()))
  
  # Perf region_name
  expect_equal(add_super_region_name(data.table('ihme_loc_id' = c('R2'), 'super_region_name' = c('Central Europe, Eastern Europe, and Central Asia'))),
               data.table('ihme_loc_id' = c('R2'), 'super_region_name' = c('Central Europe, Eastern Europe, and Central Asia')))
  
  # Proper use by ihme_loc_id
  df <- data.table('ihme_loc_id' = c('R2'))
  expect_equal(add_super_region_name(df)$super_region_name, 'Central Europe, Eastern Europe, and Central Asia')
  
  # Proper use by location_id
  df <- data.table('location_id' = c(32))
  expect_equal(add_super_region_name(df)$super_region_name, 'Central Europe, Eastern Europe, and Central Asia')
  
  # Proper use by location_name
  df <- data.table('location_name' = c('Central Asia'))
  expect_equal(add_super_region_name(df)$super_region_name, 'Central Europe, Eastern Europe, and Central Asia')
  
  # Proper use by region_id
  df <- data.table('region_id' = c(32))
  expect_equal(add_super_region_name(df)$super_region_name, 'Central Europe, Eastern Europe, and Central Asia')
  
  # Proper use by region_name
  df <- data.table('region_name' = c('Central Asia'))
  expect_equal(add_super_region_name(df)$super_region_name, 'Central Europe, Eastern Europe, and Central Asia')
  
  # Proper use by super_region_id
  df <- data.table('super_region_id' = c(31))
  expect_equal(add_super_region_name(df)$super_region_name, 'Central Europe, Eastern Europe, and Central Asia')
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_super_region_name(df))), 2)
})
#--------------------------------------# ####

#----# Test Add Loc Lancet Label #----# ####
test_that('Add Loc Lancet Label', {
  # Bad expected cols
  expect_error(add_loc_lancet_label(data.table()))
  
  # Perf lancet_label
  expect_equal(add_loc_lancet_label(data.table('location_id' = c(1), 'lancet_label' = c('Global'))), 
               data.table('location_id' = c(1), 'lancet_label' = c('Global')))
  
  # Proper use by ihme_loc_id
  df <- data.table('ihme_loc_id' = c('G'))
  expect_equal(add_loc_lancet_label(df)$lancet_label, 'Global')
  
  # Proper use by location_id
  df <- data.table('location_id' = c(1))
  expect_equal(add_loc_lancet_label(df)$lancet_label, 'Global')
  
  # Proper use by location_name
  df <- data.table('location_name' = c('Global'))
  expect_equal(add_loc_lancet_label(df)$lancet_label, 'Global')
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_loc_lancet_label(df))), 2)
})
#-------------------------------------# ####

#----# Test Add Loc WHO Label #----# ####
test_that('Add Loc WHO Label', {
  # Bad expected cols
  expect_error(add_loc_who_label(data.table()))
  
  # Perf lancet_label
  expect_equal(add_loc_who_label(data.table('location_id' = c(1), 'who_label' = c('Global'))), 
               data.table('location_id' = c(1), 'who_label' = c('Global')))
  
  # Proper use by ihme_loc_id
  df <- data.table('ihme_loc_id' = c('G'))
  expect_equal(add_loc_who_label(df)$who_label, 'Global')
  
  # Proper use by location_id
  df <- data.table('location_id' = c(1))
  expect_equal(add_loc_who_label(df)$who_label, 'Global')
  
  # Proper use by location_name
  df <- data.table('location_name' = c('Global'))
  expect_equal(add_loc_who_label(df)$who_label, 'Global')
  
  # Proper use no extra cols
  expect_equal(length(colnames(add_loc_who_label(df))), 2)
})
#----------------------------------# ####

rm(list=ls())