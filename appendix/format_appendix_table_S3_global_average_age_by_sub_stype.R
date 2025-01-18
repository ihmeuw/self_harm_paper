rm(list=ls())
source("/FILEPATH/get_cause_metadata.R")
source("/FILEPATH/get_rei_metadata.R")
source("/FILEPATH/get_outputs.R")
source("/FILEPATH/get_location_metadata.R")
source("/FILEPATH/get_covariate_estimates.R")
source("/FILEPATH/get_pct_change.R")
source("/FILEPATH/get_sequela_metadata.R")
source("/FILEPATH/get_age_metadata.R")
source("/FILEPATH/get_draws.R")
source("/FILEPATH/get_ids.R")

library(tidyverse)
library(reshape2)
# library(writexl)
library(grid)
library(gridExtra)
library(RColorBrewer)
library(scales)
library(ggplot2)
library(data.table)
library(stringr)


library(data.table)
library(tidyr)
library(openxlsx)
library(dplyr)

#--------- Set up Lancet fonts --------------
# Defines the font families
# f3 is the standard Lancet font
f1 <- "Times"
f2 <- "ScalaLancetPro"
f3 <- "Shaker 2 Lancet Regular"
source(paste0("/FILEPATH/", Sys.getenv("USER"), "/FILEPATH/as_capstone_table.R"))
OUT_DIR = "/FILEPATH/"
df <- read.csv("/FILEPATH/appendix_table_global_average_age_of_death_by_sub_cause.csv")

df_names <- names(df)[grep("val.", names(df), fixed = T)]
titles <- tstrsplit(gsub("val.", "",df_names, fixed = T), ".", fixed = T)
title2 <- unlist(titles[2])
title2[1:length(title2) %% 2 == 0] <- ""

title2 = t(c("", title2))

title1 <- unlist(titles[1])

title1 = t(c("location_name", title1))
setnames(df, "location_name", "Location")

# must run in Rstudio session. function tries to display table before saving
as_capstone_table(df,
                  label = "Location",
                  title1 = title1,
                  title2 = title2,
                  non.numeric = F,
                  with.ui = T,
                  hierarchy = F,
                  order = F,
                  alternate = T, 
                  lancet_font = T, 
                  outfile = paste0("/FILEPATH/appendix_table_formatted_global_average_age_of_death_by_sub_cause", ".xlsx"))

