#----# INFO #----# ####
# Script : test_data_man_calc.R
# Description: Automated testing of Data Manipulation and Calculation functions
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

#----# Test NI #----# ####
test_that('Test NI', {
  expect_equal('q' %ni% 'this', T)
})
#-------------------# ####

#----# Test Collapse #----# ####
test_that('Test Collapse', {
  df <- data.table('year' = c(2020, 2020), 'num' = c(1, 2))
  
  # Bad group_cols
  expect_error(collapse(df, 'sum', 'yr', 'num'))
  
  # Bad calc_cols
  expect_error(collapse(df, 'sum', 'year', 'vlue'))
  
  # Proper use
  expect_equal(collapse(df, 'sum', 'year', 'num')$num, 3)
})
#-------------------------# ####

#----# Test Rowtotal #----# ####
test_that('Test Rowtotal', {
  df <- data.table('year' = c(2020, 2020), 'r1' = c(1, 2), 'r2' = c(1,2))
  
  # Existing column name
  expect_error(rowtotal(df, 'year', c('r1', 'r2')))
  
  # Bad rowtotal_cols
  expect_error(rowtotal(df, 'sum', c('r1', 'r3')))
  
  # Proper use
  expect_equal(rowtotal(df, 'sum', c('r1', 'r2'))$sum, c(2,4))
})
#-------------------------# ####

#----# Test Aggregate Long Draws #----# ####
test_that('Aggregate Long Draws', {
  df = data.table(
    'year' = c(2019, 2019, 2020, 2020),
    'location_id' = c(1, 1, 1, NA),
    'draw_num' = c(0,1,0,1),
    'draw_val' = c(0, 1, 0, NA)
  )
  
  # Bad id_cols
  expect_error(aggregate_long_draws(df, 'nope', 'draw_num'))
  
  # NA id_cols values
  expect_error(aggregate_long_draws(df, 'location_id', 'draw_num'))
  
  # Bad value_col
  expect_error(aggregate_long_draws(df, 'year', 'nope'))
  
  # NA value_col values
  expect_error(aggregate_long_draws(df, 'year', 'draw_val'))
  
  df = data.table(
    'year' = c(2019, 2019, 2020, 2020),
    'location_id' = c(1, 1, 1, 1),
    'draw_num' = c(1,2,1,2),
    'draw_val' = c(0, 1, 0, 1)
  )
  
  # Proper use
  expect_equal(aggregate_long_draws(df, c('year', 'location_id'), 'draw_val')$lower, c(0.025, 0.025))
})
#-------------------------------------# ####

#----# Test Aggregate Wide Draws #----# ####
test_that('Aggregate Wide Draws', {
  df <- data.table('year' = c(2019, 2020),
                   'location_id' = c(1, 1),
                   'draw_1' = c(0,0),
                   'draw_2' = c(1,NA))
  
  # Bad draw_col_stub
  expect_error(aggregate_wide_draws(df, 'drw'))
  
  # NA draw_col_stub values
  expect_error(aggregate_wide_draws(df, 'draw_'))
  
  df <- data.table('year' = c(2019, 2020),
                   'location_id' = c(1, 1),
                   'draw_1' = c(0,0),
                   'draw_2' = c(1,1))
  
  # Proper use
  expect_equal(aggregate_wide_draws(df, 'draw_')$lower, c(0.025, 0.025))
  expect_equal(aggregate_wide_draws(df, 'draw_')$mean, c(0.5, 0.5))
  expect_equal(aggregate_wide_draws(df, 'draw_')$upper, c(0.975, 0.975))
  
})
#-------------------------------------# ####

rm(list=ls())