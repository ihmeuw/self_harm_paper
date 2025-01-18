rm(list=ls())
library(RColorBrewer)
library(maptools)
require(sp)
library(ggplotify)
library(ggplot2)
library(cowplot)
library(patchwork)


df = read.csv("/FILEPATH/table_5_age_groups_avg_5_years_country_level.csv")

extract_age_dataframe <- function(df, val_column){
  df <- df[c("location_id","location_name",'sex_id','sex_id','cause_id', val_column)]
  df = df %>% drop_na()
  names(df)[names(df) == val_column] <- 'mapvar'
  df = df[df$cause_id == 718,]
  df_male = df[df$sex_id == 1,]
  df_female = df[df$sex_id == 2,]
  
  return (list(df_male, df_female))
}

dfs_10_29 = extract_age_dataframe(df, 'val.mr_rate_10_to_29')
df_male_10_29 = dfs_10_29[[1]]
df_female_10_29 = dfs_10_29[[2]]

dfs_30_49 = extract_age_dataframe(df, 'val.mr_rate_30_to_49')
df_male_30_49 = dfs_30_49[[1]]
df_female_30_49 = dfs_30_49[[2]]

dfs_50_69 = extract_age_dataframe(df, 'val.mr_rate_50_to_69')
df_male_50_69 = dfs_50_69[[1]]
df_female_50_69 = dfs_50_69[[2]]

dfs_70_plus = extract_age_dataframe(df, 'val.mr_rate_70_plus')
df_male_70_plus = dfs_70_plus[[1]]
df_female_70_plus = dfs_70_plus[[2]]

mapcolors <-  c("#0d4e93", "#0095c0", "#add9eb", "#e9f5f3", 
                "#feeb98",  "#fdcd7b", "#f89c59",
                "#ec6445", "#e22527", "#b31f39")


make_subplot <- function(df, title, map_colors, sex){
  data <- as.data.frame(df)
  
  data$loc_id <- data$location_id
  data$location_id <- NULL
  pattern=NULL
  na.color = "grey70"
  
  col <- mapcolors
  
  if (sex == 'male'){
    limits = c(0, 3, 6, 9, 16, 25, 40, 60, 90, 120, 1000)
  } else {
    limits = c(0, 1, 2, 3, 4, 5, 10, 15, 25, 40, 1000)
  }
  
  n <- length(limits) - 1
  
  load("/FILEPATH/2021GBD_PREPPED_DATA_MAP.RData")
  main_data <- merge(data, map@data[,c("loc_id", "ID")], by="loc_id", sort= TRUE, all.y=T)
  kmlPolygon(border=.01)
  
  load("/FILEPATH/2021GBD_PREPPED_DATA_NOSUBMAP.RData")
  nat_map <- merge(data, nosubmap@data[,c("loc_id", "ID")],by="loc_id", sort= TRUE, all.y=T)
  kmlPolygon(border=.01)
  
  load("/FILEPATH/2021GBD_PREPPED_DISPUTED_DATA.RData")
  disputed_data <- merge(data, disputed@data[,c("ADM0_NAME", "ID", "DISP_AREA")], all.y=T)
  kmlPolygon(border=.01)
  
  load("/FILEPATH/2021GBD_PREPPED_DISPUTED_BORDER_DATA.RData")
  disputed_border@data$linetype <- ifelse(disputed_border@data$DISP_AREA==1,2,1)
  disputed_border_non <- disputed_border[disputed_border@data$DISP_AREA==0,]
  kmlPolygon(border=.01)
  disputed_border <-disputed_border[disputed_border@data$DISP_AREA==1,]
  kmlPolygon(border=.01)
  
  disputed_border_map <- fortify(disputed_border)
  
  ## assign colors and patterns
  main_data$color <- main_data$pattern <- NA
  n <- length(limits) - 1
  if (is.null(pattern)) pattern <- rep(0, n)
  
  nat_map$color = NA
  nat_map$pattern = NA
  
  if (sex == "male"){
    for (g in 1:n) {
      ii <- (main_data$mapvar >= limits[g] & main_data$mapvar < limits[g+1])
      main_data$lower_bound[ii] = limits[g]
      main_data$upper_bound[ii] = limits[g+1]
      if (g == 1){
        main_data$legend[ii] = "Less than 3"
      } else if (g == 10){
        main_data$legend[ii] = "120 or Greater"
      } else {
        main_data$legend[ii] = paste0(limits[g]," to <", limits[g+1])
      }
      
      main_data$color[ii] <- mapcolors[g]
      main_data$pattern[ii] <- pattern[g]
    }
  } else {
    for (g in 1:n) {
      ii <- (main_data$mapvar >= limits[g] & main_data$mapvar < limits[g+1])
      main_data$lower_bound[ii] = limits[g]
      main_data$upper_bound[ii] = limits[g+1]
      if (g == 1){
        main_data$legend[ii] = "Less than 1"
      } else if (g == 10){
        main_data$legend[ii] = "40 or Greater"
      } else {
        main_data$legend[ii] = paste0(limits[g]," to <", limits[g+1])
      }
      
      main_data$color[ii] <- mapcolors[g]
      main_data$pattern[ii] <- pattern[g]
    }
  }
  
  main_data$color[is.na(main_data$color)] <- na.color
  main_data$pattern[is.na(main_data$pattern)] <- 0
  
  main_data$density <- ifelse(main_data$pattern==0, 0, 30)
  main_data$angle <- as.numeric(as.character(factor(main_data$pattern, levels=1:4, label=c(0,45,90,135))))

  if (is.null(labels)) {
    for (g in 1:n) {
      labels <- c(labels, paste(limits[g], " to ", limits[g+1]))
    }
  }
  
  map <- fortify(nosubmap)
  
  map$ID = as.numeric(as.character(map$id))
  
  map = map %>% left_join(main_data, by = c("ID" = "ID"))
  
  if (sex == 'male'){
    map$legend = factor(map$legend, levels=c(
      "Less than 3",
      "3 to <6",
      "6 to <9",
      "9 to <16",
      "16 to <25",
      "25 to <40",
      "40 to <60",
      "60 to <90",
      "90 to <120",
      "120 or Greater"
    ))
  } else {
    map$legend = factor(map$legend, levels=c(
      "Less than 1",
      "1 to <2",
      "2 to <3",
      "3 to <4",
      "4 to <5",
      "5 to <10",
      "10 to <15",
      "15 to <25",
      "25 to <40",
      "40 or Greater"
    ))
  }
  
  plt = ggplot() +
    geom_polygon(data=map,
                 aes(x=long, y=lat, group=group, fill=legend), color='black', show.legend=TRUE
    ) +
    scale_fill_manual(values = mapcolors, drop=FALSE, name="Mortality Rate Per 100k") + theme(
      panel.background = element_rect(fill = "transparent"),
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank()
    )+
    theme_void() + 
    ggtitle(title)
  
  plt = plt + geom_path(data=disputed_border_map, aes(x=long, y=lat, group=group), color='white', cex=.5, lty=1, lwd=.3)
  plt = plt + geom_path(data=disputed_border_map, aes(x=long, y=lat, group=group), color='grey29', cex=.5, lty=2, lwd=.2)
  return (plt)
}


#####
pdf("/FILEPATH/custom_age_group_map_males.pdf", width=14, height=8)

plt_male_10_29 = make_subplot(df_male_10_29, "Age: 10 to 29", mapcolors, "male")
plt_male_30_49 = make_subplot(df_male_30_49, "Age: 30 to 49", mapcolors, "male")
plt_male_50_69 = make_subplot(df_male_50_69, "Age: 50 to 69", mapcolors, "male")
plt_male_70_plus = make_subplot(df_male_70_plus, "Age: 70 Plus", mapcolors, "male")

pw = (
  (plt_male_10_29 + theme(legend.position="none")) + 
  (plt_male_30_49 + theme(legend.position="none"))
  ) / (
  (plt_male_50_69 + theme(legend.position="none")) + 
  plt_male_70_plus) 

pw + plot_annotation(
  title="Male Mortality Rate by Age Group",
  subtitle="Average from 2017 to 2021"
) + plot_layout(guides = "collect")

dev.off()


pdf("/FILEPATH/custom_age_group_map_females.pdf", width=14, height=8)

plt_female_10_29 = make_subplot(df_female_10_29, "Age: 10 to 29", mapcolors, "female")
plt_female_30_49 = make_subplot(df_female_30_49, "Age: 30 to 49", mapcolors, "female")
plt_female_50_69 = make_subplot(df_female_50_69, "Age: 50 to 69", mapcolors, "female")
plt_female_70_plus = make_subplot(df_female_70_plus, "Age: 70 Plus", mapcolors, "female")

pw = (
  (plt_female_10_29 + theme(legend.position="none")) + 
    (plt_female_30_49 + theme(legend.position="none"))
) / (
  (plt_female_50_69 + theme(legend.position="none")) + 
    plt_female_70_plus) 

pw + plot_annotation(
  title="Female Mortality Rate by Age Group",
  subtitle="Average from 2017 to 2021"
) + plot_layout(guides = "collect")
dev.off()


