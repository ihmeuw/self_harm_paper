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

f1 <- "Times"
f2 <- "ScalaLancetPro"
f3 <- "Shaker 2 Lancet Regular"
source(paste0("/FILEPATH/as_capstone_table.R"))
source(paste0("/FILEPATH/as_lancet_table.R"))
OUT_DIR = "/FILEPATH/"
df <- read.csv("/FILEPATH/table_S9_average_age_1990_2021.csv")

df_names <- names(df)[grep("val.", names(df), fixed = T)]
titles <- tstrsplit(gsub("val.", "",df_names, fixed = T), ".", fixed = T)
title2 <- unlist(titles[2])
title2[1:length(title2) %% 2 == 0] <- ""

title2 = t(c("", title2))

title1 <- unlist(titles[1])

title1 = t(c("location_name", title1))
setnames(df, "location_name", "Location")

as_lancet_table(df,
    label = "Location",
    hierarchy = T, 
    sdi = T, 
    alternate = F,
    rounded = T,
    with.ui = T,
    non.numeric = F,
    title = title1,
    lancet_font = T, 
    outfile = paste0("/FILEPATH/appendix_table_S9_average_age_1990_2021", ".xlsx"))

