#----# INFO #----# ####
# Script : utils.R
# Contents: get_core_ref, get_root, set_roots, %ni%, collapse, rowtotal, 
#           aggregate_long_draws, aggregate_wide_draws, add_ihme_loc_id,
#           add_location_name, add_region_id, add_region_name,
#           add_super_region_id, add_super_region_name, add_loc_lancet_label,
#           add_loc_who_label, add_cause_id, add_acause, add_cause_name, 
#           add_cause_lancet_label, launch_qsub
# Description: Contains useful functions for data formatting, including 
#              R versions of common STATA commands.
# Contributors: Kyle Simpson
#----------------# ####

#----# Load Required Libraries #----# ####
pacman::p_load(yaml, data.table, tidyverse) 

if (!exists(".code_repo"))  {
  .code_repo <- unname(ifelse(Sys.info()['sysname'] == "Windows", "H:/repos/surge_utils/", paste0("/ihme/homes/", Sys.info()['user'][1], "/repos/surge_utils/")))
}
#-----------------------------------# ####

#----# Root and Path Helpers #----# ####
get_core_ref <- function(param_name, sub_key=NULL) {
  #' Convenience function to pull static reference from refs.yaml
  #' @param param_name [str]: A string containing the reference desired
  #' @param sub_key [str]: (OPTIONAL) A string containing the sub-reference needed
  
  # Error handling
  if (is.null(param_name)) {
    stop('Supplied param_name is None. You must supply a value.')
  }
  
  f <- yaml.load_file(paste0(.code_repo, "refs.yaml"))[[param_name]]
   
  if (is.null(sub_key)) {
    return(f)
  } else {
    return(f[[sub_key]])
  }
}

.get_root <- function(root) {
  #' Internal function to pull a specific root
  #' @param root [str] Name of root to pull (j, h, k, share)
  
  os <- Sys.info()['sysname']
  
  if (root == 'j') {
    if (os == 'Windows') {
      return('J:/')
    } else {
      return ('/home/j/')
    }
  } else if (root == 'h') {
    if (os == 'Windows') {
      return('H:/')
    } else {
      return (paste0('/ihme/homes/', Sys.info()['user'][1], '/'))
    }
  } else if (root == 'k') {
    if (os == 'Windows') {
      return('K:/')
    } else {
      return ('/ihme/cc_resources/')
    }
  } else if (root == 'share') {
    if (os == 'Windows') {
      return('')
    } else {
      return('/ihme/')
    }
  }
}

.set_roots <- function() {
  #' Internal function to create root filepaths.
  
  roots <- list(
    'j' = .get_root('j'), 
    'h' = .get_root('h'), 
    'k' = .get_root('k'), 
    'share' = .get_root('share'), 
    'gbd_round' = get_core_ref('gbd_round_id'),
    'gbd_year' = get_core_ref('gbd_year')
  )
  
  roots <<- roots
  return(roots)
}

.set_roots()
#---------------------------------# ####

#----# Data Manipulation and Calculation Functions #----# ####
`%ni%` <- Negate(`%in%`)

collapse <- function(df, agg_function='sum', group_cols, calc_cols) {
  #' Convenience function for STATA-like collapsing. Like STATA, removes any columns not specified in either group_cols or calc_cols.
  #' @param df [data.frame/data.table] Dataset intended to be collapsed
  #' @param agg_function [str] The name of the aggregate function wished to be performed
  #' @param group_cols [vector] A list of the column names you wish to group by
  #' @param calc_cols [vector] A list of the column names you wish to collapse
  
  # Error handling
  if (any(group_cols %ni% colnames(df))) {
    stop('One or more supplied group_cols not in df columns.')
  }
  if (any(calc_cols %ni% colnames(df))) {
    stop('One or more supplied calc_cols not in df columns.')
  }
  
  # Convert to data.table
  dataset <- setDT(copy(df))
  
  # Lapply the aggregate function over the specified columns, by any grouping
  dataset <- dataset[, lapply(.SD, get(agg_function), na.rm=T), by=c(group_cols), .SDcols=c(calc_cols)]
  
  # Return the dataset
  return(dataset)
}

rowtotal <- function(df, new_colname, rowtotal_cols) {
  #' Convenience function to perform STATA-like row total
  #' @param df [data.frame/data.table] Dataset intended to be collapsed
  #' @param new_colname [str] The name of the new column to be calculated
  #' @param rowtotal_cols [vector] A list of the column names you wish to sum
  
  # Error handling
  if (new_colname %in% colnames(df)) {
    stop('Supplied new_colname already exists in df.')
  }
  if (any(rowtotal_cols %ni% colnames(df))) {
    stop('One or more supplied rowtotal_cols are missing in df.')
  }
  
  # Convert to data.table
  dataset <- setDT(copy(df))
  
  # rowSums the specified columns
  dataset[, eval(new_colname) := rowSums(dataset[, c(rowtotal_cols), with=F], na.rm=T)]
  
  # Return dataset
  return(dataset)
}

aggregate_long_draws <- function(df, id_cols, value_col) {
  #' Convenience function which aggregates draws in long format
  #' @param df [data.table/data.frame] 
  #' @param id_cols [str/vector] A single column name, or multiple which uniquely identify rows.
  #' @param value_cols [str] A single column name identifying draw values.
  
  # Error handling
  if (any(id_cols %ni% colnames(df))) {
    stop('One or more supplied id_cols missing from df columns.')
  }
  for (col in id_cols) {
    if (any(is.na(df[[col]]))) {
      stop(paste0('Values in ', col, ' contain NAs. Please fix.'))
    }
  }
  if (value_col %ni% colnames(df)) {
    stop('Supplied value_col missing from df columns.')
  }
  if (any(is.na(df[[value_col]]))) {
    stop('Values in value_col contain NAs. Please fix.')
  }
  
  t <- df[, as.list(c(mean(get(value_col)), quantile(get(value_col), c(0.025, 0.975)))), by = id_cols]
  colnames(t) <- c(id_cols, "mean", "lower", "upper")
  
  return(t)
}

aggregate_wide_draws <- function(df, draw_col_stub) {
  #' Convenience function which aggregates draws in wide format
  #' @param df [data.table/data.frame]
  #' @param draw_col_stub [str] A stub matching each column containing draws
  
  # Error handling
  if (length(colnames(df)[colnames(df) %like% draw_col_stub]) == 0) {
    stop('Supplied draw_col_stub not found in df column names.')
  }
  for (col in names(df)[names(df) %like% draw_col_stub]) {
    if (any(is.na(df[[col]]))) {
      stop(paste0('Values in ', col, ' contain NAs. Please fix.'))
    }
  }
  
  # Convert to data.table
  dataset <- setDT(copy(df))
  
  keep_cols <- names(dataset)[!(names(dataset) %like% draw_col_stub)]
  calc_cols <- names(dataset)[names(dataset) %like% draw_col_stub]
  
  dataset$lower <- dataset[, c(calc_cols), with=F] %>% apply(1, quantile, 0.025)
  dataset$mean <- dataset[, c(calc_cols), with=F] %>% apply(1, mean)
  dataset$upper <- dataset[, c(calc_cols), with=F] %>% apply(1, quantile, 0.975)
  
  dataset <- dataset[, c(keep_cols, 'lower', 'mean', 'upper'), with=F]
  
  return(dataset)
}
#-------------------------------------------------------# ####

#----# GBD Location Tools #----# ####
add_ihme_loc_id <- function(df) {
  #' Convenience function which returns data.table with ihme_loc_id column
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('location_id', 'location_name') %ni% colnames(df))) {
    stop('Supplied df does not contain columns for location_id or location_name.')
  }
  if ('ihme_loc_id' %in% colnames(df)) {
    if (all(!is.na(df$ihme_loc_id))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_location_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'ihme_loc_id')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('location_id','location_name','ihme_loc_id')
  locs <- get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[, c(meta_cols), with=F]
  
  if ('location_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_id', all.x=T)
  } else {
    t <- merge(dt, locs, by='location_name', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}

add_location_name <- function(df) {
  #' Convenience function which returns a data.table with location_name column
  #' @param df [data.table/data.frame]
  
  # Error handing
  if (all(c('ihme_loc_id', 'location_id') %ni% colnames(df))) {
    stop('Supplied df does not contain column for ihme_loc_id or location_id.')
  }
  if ('location_name' %in% colnames(df)) {
    if (all(!is.na(df$location_name))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_location_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'location_name')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('ihme_loc_id','location_id','location_name')
  locs <- get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[, c(meta_cols), with=F]
  
  if ('ihme_loc_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='ihme_loc_id', all.x=T)
  } else {
    t <- merge(dt, locs, by='location_id', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}

add_region_id <- function(df) {
  #' Convenience function which returns a data.table with region_id
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('ihme_loc_id','location_id','location_name','region_name') %ni% colnames(df))) {
    stop('Supplied df does not contain column for ihme_loc_id, location_id, location_name, or region_name.')
  }
  if ('region_id' %in% colnames(df)) {
    if (all(!is.na(df$region_id))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_location_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'region_id')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('ihme_loc_id','location_id','location_name', 'region_name', 'region_id')
  locs <- get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[, c(meta_cols), with=F]
  
  if ('ihme_loc_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='ihme_loc_id', all.x=T)
  } else if ('location_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_id', all.x=T)
  } else if ('location_name' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_name', all.x=T)
  } else {
    t <- merge(dt, distinct(locs[, c('region_name', 'region_id')]), by='region_name', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}

add_region_name <- function(df) {
  #' Convenience function which returns a data.table with region_name column
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('ihme_loc_id','location_id','location_name','region_id') %ni% colnames(df))) {
    stop('Supplied df does not contain column for ihme_loc_id, location_id, location_name, or region_id')
  }
  if ('region_name' %in% colnames(df)) {
    if (all(!is.na(df$region_name))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_location_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'region_name')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('ihme_loc_id','location_id','location_name', 'region_id', 'region_name')
  locs <- get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[, c(meta_cols), with=F]
  
  if ('ihme_loc_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='ihme_loc_id', all.x=T)
  } else if ('location_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_id', all.x=T)
  } else if ('location_name' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_name', all.x=T)
  } else {
    t <- merge(dt, distinct(locs[, c('region_id', 'region_name')]), by='region_id', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}

add_super_region_id <- function(df) {
  #' Convenience function which returns a data.table with superregion_id column
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('ihme_loc_id', 'location_id','location_name',
            'region_id','region_name','super_region_name') %ni% colnames(df))) {
    stop('Supplied df does not contain column for ihme_loc_id, location_id, location_name, region_id, region_name, or super_region_name.')
  }
  if ('super_region_id' %in% colnames(df)) {
    if (all(!is.na(df$super_region_id))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_location_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'super_region_id')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('ihme_loc_id','location_id','location_name', 'region_id', 'region_name', 'super_region_id', 'super_region_name')
  locs <- get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[, c(meta_cols), with=F]
  
  if ('ihme_loc_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='ihme_loc_id', all.x=T)
  } else if ('location_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_id', all.x=T)
  } else if ('location_name' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_name', all.x=T)
  } else if ('region_id' %in% colnames(dt)) {
    t <- merge(dt, distinct(locs[, c('region_id', 'super_region_id')]), by='region_id', all.x=T)
  } else if ('region_name' %in% colnames(dt)) {
    t <- merge(dt, distinct(locs[, c('region_name', 'super_region_id')]), by='region_name', all.x=T)
  } else {
    t <- merge(dt, distinct(locs[, c('super_region_name', 'super_region_id')]), by='super_region_name', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}

add_super_region_name <- function(df) {
  #' Convenience function which returns a data.table with superregion_name column
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('ihme_loc_id', 'location_id','location_name',
            'region_id','region_name','super_region_id') %ni% colnames(df))) {
    stop('Supplied df does not contain column for ihme_loc_id, location_id, location_name, region_id, region_name, or super_region_id.')
  }
  if ('super_region_name' %in% colnames(df)) {
    if (all(!is.na(df$super_region_name))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_location_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'super_region_name')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('ihme_loc_id','location_id','location_name', 'region_id', 'region_name', 'super_region_id', 'super_region_name')
  locs <- get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[, c(meta_cols), with=F]
  
  if ('ihme_loc_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='ihme_loc_id', all.x=T)
  } else if ('location_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_id', all.x=T)
  } else if ('location_name' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_name', all.x=T)
  } else if ('region_id' %in% colnames(dt)) {
    t <- merge(dt, distinct(locs[, c('region_id', 'super_region_name')]), by='region_id', all.x=T)
  } else if ('region_name' %in% colnames(dt)) {
    t <- merge(dt, distinct(locs[, c('region_name', 'super_region_name')]), by='region_name', all.x=T)
  } else {
    t <- merge(dt, distinct(locs[, c('super_region_name', 'super_region_id')]), by='super_region_id', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}

add_loc_lancet_label <- function(df) {
  #' Convenience function which returns a data.table with lancet_label column.
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('ihme_loc_id', 'location_id', 'location_name') %ni% colnames(df))) {
    stop('Supplied df is missing column for ihme_loc_id, location_id, or location_name.')
  }
  if ('lancet_label' %in% colnames(df)) {
    if (all(!is.na(df$lancet_label))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_location_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'lancet_label')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('ihme_loc_id','location_id','location_name', 'lancet_label')
  locs <- get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[, c(meta_cols), with=F]
  
  if ('ihme_loc_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='ihme_loc_id', all.x=T)
  } else if ('location_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_id', all.x=T)
  } else {
    t <- merge(dt, locs, by='location_name', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}

add_loc_who_label <- function(df) {
  #' Convenience function which returns a data.table with who_label column.
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('ihme_loc_id', 'location_id', 'location_name') %ni% colnames(df))) {
    stop('Supplied df is missing column for ihme_loc_id, location_id, or location_name.')
  }
  if ('who_label' %in% colnames(df)) {
    if (all(!is.na(df$who_label))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_location_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'who_label')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('ihme_loc_id','location_id','location_name', 'who_label')
  locs <- get_location_metadata(location_set_id=1, gbd_round_id=gbd_rid, decomp_step=d_step)[, c(meta_cols), with=F]
  
  if ('ihme_loc_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='ihme_loc_id', all.x=T)
  } else if ('location_id' %in% colnames(dt)) {
    t <- merge(dt, locs, by='location_id', all.x=T)
  } else {
    t <- merge(dt, locs, by='location_name', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}
#------------------------------# ####

#----# GBD Cause Tools #----# ####
add_cause_id <- function(df){
  #' Convenience function which returns a data.table with cause_id column
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('acause', 'cause_name') %ni% colnames(df))) {
    stop('Supplied df does not contain column for acause or cause_name.')
  }
  if ('cause_id' %in% colnames(df)) {
    if (all(!is.na(df$cause_id))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_cause_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'cause_id')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('cause_id', 'acause', 'cause_name')
  causes <- get_cause_metadata(cause_set_id = 3, gbd_round_id = gbd_rid, decomp_step = d_step)[, c(meta_cols), with=F]
  
  if ('acause' %in% colnames(dt)) {
    t <- merge(dt, causes, by='acause', all.x=T)
  } else {
    t <- merge(dt, causes, by='cause_name', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}

add_acause <- function(df) {
  #' Convenience function which returns a data.table with acause column
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('cause_id', 'cause_name') %ni% colnames(df))) {
    stop('Supplied df does not contain column for cause_id or cause_name.')
  }
  if ('acause' %in% colnames(df)) {
    if (all(!is.na(df$acause))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_cause_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'acause')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('cause_id', 'acause', 'cause_name')
  causes <- get_cause_metadata(cause_set_id = 3, gbd_round_id = gbd_rid, decomp_step = d_step)[, c(meta_cols), with=F]
  
  if ('cause_id' %in% colnames(dt)) {
    t <- merge(dt, causes, by='cause_id', all.x=T)
  } else {
    t <- merge(dt, causes, by='cause_name', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}

add_cause_name <- function(df) {
  #' Convenience function which returns a data.table with cause_name column
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('cause_id', 'acause') %ni% colnames(df))) {
    stop('Supplied df does not contain column for cause_id or acause.')
  }
  if ('cause_name' %in% colnames(df)) {
    if (all(!is.na(df$cause_name))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_cause_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'cause_name')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('cause_id', 'acause', 'cause_name')
  causes <- get_cause_metadata(cause_set_id = 3, gbd_round_id = gbd_rid, decomp_step = d_step)[, c(meta_cols), with=F]
  
  if ('cause_id' %in% colnames(dt)) {
    t <- merge(dt, causes, by='cause_id', all.x=T)
  } else {
    t <- merge(dt, causes, by='acause', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}

add_cause_lancet_label <- function(df) {
  #' Convenience function which returns a data.table with lancet_label column
  #' @param df [data.table/data.frame]
  
  # Error handling
  if (all(c('cause_id', 'acause', 'cause_name') %ni% colnames(df))) {
    stop('Supplied df does not contain column for cause_id, acause, or cause_name.')
  }
  if ('lancet_label' %in% colnames(df)) {
    if (all(!is.na(df$lancet_label))) {
      return(df)
    }
  }
  
  source(paste0(.get_root('k'), 'libraries/current/r/get_cause_metadata.R'))
  
  dt <- setDT(copy(df))
  
  ret_cols <- c(colnames(dt), 'lancet_label')
  gbd_rid <- get_core_ref('gbd_round_id')
  d_step <- get_core_ref('decomp_step')
  meta_cols <- c('cause_id', 'acause', 'cause_name', 'lancet_label')
  causes <- get_cause_metadata(cause_set_id = 3, gbd_round_id = gbd_rid, decomp_step = d_step)[, c(meta_cols), with=F]
  
  if ('cause_id' %in% colnames(dt)) {
    t <- merge(dt, causes, by='cause_id', all.x=T)
  } else if ('acause' %in% colnames(dt)) {
    t <- merge(dt, causes, by='acause', all.x=T)
  } else {
    t <- merge(dt, causes, by='cause_name', all.x=T)
  }
  
  # Remove non-required cols
  t <- t[, c(ret_cols), with=F]
  return(t)
}
#---------------------------# ####

#----# QSUB Helpers #----# ####
launch_qsub <- function(errors_path=.get_root('h'), output_path=.get_root('h'), job_name=NULL, queue='i.q', 
                        cluster_project='ihme_general', num_threads=NULL, num_gigs=NULL, runtime=NULL, 
                        script_path=NULL, script_language='r', extra_args=NULL) {
  #' Convenience function to launch a qsub on the cluster
  #' @param errors_path [str] String filepath to desired errors file.
  #' @param output_path [str] String filepath to desired output file.
  #' @param job_name [str] String name of the job to be launched.
  #' @param queue [str] String name of the queue the job should be launched in. E.x. i.q, all.q, long.q, etc..
  #' @param cluster_project [str] String name of the cluster project the job should be launched under.
  #' @param num_threads [int] Number of threads needed for the job.
  #' @param num_gigs [int] Number of threads needed for the job.
  #' @param runtime [str] String representation of time in HH:MM:SS the job requires to complete.
  #' @param script_path [str] A string containing the full filepath to the script to be launched.
  #' @param script_language [str] A string containing the name of the language of the script to be launched.
  #' @param extra_args [str/vector] An optional string/vector of extra arguments.
  
  # Error handling
  if (nchar(errors_path) == 0) {
    stop('Supplied errors_path is blank.')
  } 
  if (nchar(output_path) == 0) {
    stop('Supplied output_path is blank.')
  }
  if (is.null(job_name) | nchar(job_name) == 0) {
    stop('Supplied job_name is blank.')
  }
  if (nchar(queue) == 0) {
    stop('Supplied queue is blank.')
  }
  if (queue %ni% c('i.q', 'all.q', 'long.q', 'd.q')) {
    stop('Supplied queue is not a valid cluster queue.')
  }
  if (nchar(cluster_project) == 0) {
    stop('Supplied cluster_project is blank.')
  }
  if (is.null(num_threads) | !is.numeric(num_threads)) {
    stop('Supplied num_threads is blank or non-numeric.')
  }
  if (is.null(num_gigs) | !is.numeric(num_gigs)) {
    stop('Supplied num_gigs is blank or non-numeric.')
  }
  if (is.null(runtime) | !is.character(runtime)) {
    stop('Supplied runtime is blank or non-character.')
  }
  if (is.null(script_path) | !is.character(script_path)) {
    stop('Supplied script_path is blank or non-character.')
  }
  if (!is.character(script_language) | tolower(script_language) %ni% c('r', 'python')) {
    stop('Supplied script_language is blank or not: R, Python')
  }
  if (!is.null(extra_args)) {
    if (!is.character(extra_args) | !is.vector(extra_args)) {
      stop('Supplied extra_args are not a string or a list.')
    } 
    if (is.character(extra_args)) {
      extra_args = c(extra_args)
    }
  } else {
    extra_args = c()
  }
  
  if (tolower(script_language) == 'python') {
    shell <- paste0(.code_repo, 'shell_python.sh')
  } else {
    shell <- '/ihme/singularity-images/rstudio/shells/execRscript.sh -i /ihme/singularity-images/rstudio/ihme_rstudio_4030.img -s'
  }
  
  qsub <- paste0(
    'qsub -e ', errors_path, 'errors.txt ',
    '-o ', output_path, 'output.txt ',
    '-N ', job_name, ' ',
    '-l archive=TRUE -q ', queue, ' ',
    '-P ', cluster_project, ' ',
    '-l fthread=', num_threads,' ',
    '-l m_mem_free=', num_gigs, 'G ',
    '-l h_rt=', runtime, ' ',
    shell, ' ', 
    script_path, ' ',
    paste0(extra_args, collapse=' ')
  )
  
  cat(paste0('  ', toupper(script_language), ' job submit using ', num_gigs, ' gigs, ', num_threads, ' threads, and ', runtime, ' runtime.\n'))

  system(qsub)
}
#------------------------# ####