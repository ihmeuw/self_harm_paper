rm(list=ls())

source("/FILEPATH/get_outputs.R")
source("/FILEPATH/get_rei_metadata.R")## for pulling data
source("/FILEPATH/get_cause_metadata.R")## for pulling data
source("/FILEPATH/get_location_metadata.R") ## for pulling data
source("/FILEPATH/gbd2021_map.R")

library(tidyverse)
library(ggplot2)
library(reshape2)
library(ggpubr)
library(gridExtra)
library(scales)
library(Cairo)
library(extrafont)
library(stats)
loadfonts()
f1 <- "Times"
f2 <- "ScalaLancetPro"
f3 <- "Shaker 2 Lancet Regular"


outdir <- "/FILEPATH/"

df = read.csv("/FILEPATH/source_count_by_location_suicide.csv")


listdf = lapply(list(df), setnames, "count", "mapvar", skip_absent=TRUE)


create_breakpoints_labels = function(data) {
  # breakpoint per 10%
  create_labels = function(bkpts) {
    labels = c()
    for (i in 2:(length(bkpts))) {
      if (i == 2) {
        labels = c(labels, paste0('<', bkpts[i]))
      } else if (i == (length(bkpts))) {
        labels = c(labels, paste0(bkpts[i - 1], ">"))
      } else if (i == (length(bkpts)-1)) {
        labels = c(labels, paste0(bkpts[i-1], " to ", bkpts[i]))
      } else {
        labels = c(labels, paste0(bkpts[i-1], " to <", bkpts[i]))
      }
    }
    return(labels)
  }
  
  
  # colors for 10 standard legend items
  mapcolors <-  c("#0d4e93", "#0095c0", "#add9eb", "#e9f5f3", 
                  "#feeb98",  "#fdcd7b", "#f89c59",
                  "#ec6445", "#e22527", "#b31f39")
  
  mapcolors <- rev(mapcolors)
  
  
  breakpoint_OG <- round(quantile(unique(data$mapvar), probs = seq(0,1,0.1), na.rm = TRUE),1)
  breakpoint_OG[[1]] = breakpoint_OG[[1]] - 1
  breakpoint_OG[[11]] = breakpoint_OG[[11]] + 1
  return(list("lab_break1" =  create_labels(breakpoint_OG), "bkpt" = breakpoint_OG, "mapcolors" = mapcolors))
}

count_decimals = function(x) {
  #length zero input
  if (length(x) == 0) return(numeric())
  #count decimals
  x_nchr = x %>% abs() %>% as.character() %>% nchar() %>% as.numeric()
  x_int = floor(x) %>% abs() %>% nchar()
  x_nchr = x_nchr - 1 - x_int
  x_nchr[x_nchr < 0] = 0
  x_nchr
}

bkpts = lapply(list(df), create_breakpoints_labels)

options(OutDec="\u0B7")
pdf(paste0(outdir, "source_count_of_suicide_data.pdf"), height = 4.15, width = 7.5, pointsize = 6.5, fonts = f3)
gbd_map(data = listdf[[1]], 
        col.reverse=FALSE, 
        inset = FALSE,
        sub_nat = "none",
        limits = bkpts[[1]]$bkpt,
        labels = bkpts[[1]]$lab_break1,
        col = bkpts[[1]]$mapcolors,
        legend = T,
        legend.columns=2,
        title = "
        
        Source Count of Suicide Data",
        legend.title = "Number of Sources")  

dev.off()

