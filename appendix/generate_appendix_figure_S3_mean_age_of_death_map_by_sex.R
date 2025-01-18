rm(list=ls())
library(RColorBrewer)
library(maptools)
require(sp)
library(ggplotify)
library(ggplot2)
library(cowplot)
library(patchwork)

make_subplot <- function(df, title){
  mapcolors <-  c("#0d4e93", "#0095c0", "#add9eb", "#e9f5f3", 
                  "#feeb98",  "#fdcd7b", "#f89c59",
                  "#ec6445", "#e22527", "#b31f39")
  mapcolors <- mapcolors[10:1]
  
  data <- as.data.frame(df)
  
  # rename and set values to expected for function
  data$loc_id <- data$location_id
  data$location_id <- NULL
  pattern=NULL
  na.color = "grey70"
  
  col <- mapcolors
  
  limits = c(0, 34, 37, 40, 43, 46, 49, 52, 55, 58, 200)
  
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
  
  # need to create columns otherwise get error
  nat_map$color = NA
  nat_map$pattern = NA
  
  for (g in 1:n) {
    ii <- (main_data$mapvar >= limits[g] & main_data$mapvar < limits[g+1])
    main_data$lower_bound[ii] = limits[g]
    main_data$upper_bound[ii] = limits[g+1]
    if (g == 1){
      main_data$legend[ii] = "Less than 34"
    } else if (g == 10){
      main_data$legend[ii] = "58 or Greater"
    } else {
      main_data$legend[ii] = paste0(limits[g]," to <", limits[g+1])
    }
    
    main_data$color[ii] <- mapcolors[g]
    main_data$pattern[ii] <- pattern[g]
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
  
  map$legend = factor(map$legend, levels=c(
    "Less than 34",
    "34 to <37",
    "37 to <40",
    "40 to <43",
    "43 to <46",
    "46 to <49",
    "49 to <52",
    "52 to <55",
    "55 to <58",
    "58 or Greater"
  ))
  
  library(rgeos)
  library(rworldmap)
  wmap <- getMap(resolution="high")
  centroids <- gCentroid(wmap, byid=TRUE)
  centroids <- as.data.frame(centroids)
  centroids = cbind(location_ascii_name = rownames(centroids), centroids)
  centroids["Russia", "location_ascii_name"] <- "Russian Federation"
  centroids["Iran", "location_ascii_name"] <- "Iran (Islamic Republic of)"
  centroids["Venezuela", "location_ascii_name"] <- "Venezuela (Bolivarian Republic of)"
  centroids["Turkey", "location_ascii_name"] <- "Turkiye"
  
  area <- gArea(wmap, byid=TRUE)
  area <- as.data.frame(area)
  area = cbind(location_ascii_name = rownames(area), area)
  area["Russia", "location_ascii_name"] <- "Russian Federation"
  area["Iran", "location_ascii_name"] <- "Iran (Islamic Republic of)"
  area["Venezuela", "location_ascii_name"] <- "Venezuela (Bolivarian Republic of)"
  area["Turkey", "location_ascii_name"] <- "Turkiye"
  
  
  source("/FILEPATH/get_location_metadata.R")
  reporting_hierarchy <- get_location_metadata(location_set_id = 1, release_id=9)
  reporting_hierarchy = reporting_hierarchy[,c("location_id", "location_ascii_name")]
  
  map_stuff = merge(area, centroids, by=c("location_ascii_name"))
  
  map_stuff = merge(reporting_hierarchy, map_stuff, by=c("location_ascii_name"))
  
  map_avg_age = map[,c("loc_id", "mapvar")]
  map_avg_age = map_avg_age[!duplicated(map_avg_age), ]
  map_avg_age$location_id = map_avg_age$loc_id
  
  map_stuff = merge(map_avg_age, map_stuff, by=c("location_id"))
  
  map_stuff_filtered = map_stuff[map_stuff$area > 15,]
  
  plt = ggplot() +
    geom_polygon(data=map,
                 aes(x=long, y=lat, group=group, fill=legend), color='black', show.legend=TRUE
    ) +
    scale_fill_manual(values = mapcolors, drop=FALSE, name="Average Age of Death") + theme(
      panel.background = element_rect(fill = "transparent"),
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank()
    ) +
    geom_text(data=map_stuff_filtered, aes(x=x, y=y, label=mapvar),hjust=.3, vjust=0,  size=2) +
    theme_void() + 
    ggtitle(title)
  
  plt = plt + geom_path(data=disputed_border_map, aes(x=long, y=lat, group=group), color='white', cex=.5, lty=1, lwd=.3)
  plt = plt + geom_path(data=disputed_border_map, aes(x=long, y=lat, group=group), color='grey29', cex=.5, lty=2, lwd=.2)

  return (plt)
}

df = read.csv("/FILEPATH/self_harm_average_age_with_ui.csv")

names(df)[names(df) == "average_age"] <- 'mapvar'

df$mapvar = round(df$mapvar, 1)

df_male = df[df$sex_id == 1,]
df_female = df[df$sex_id == 2,]


male_plt = make_subplot(df_male, "(A) Average Age of Suicide, Males, 2021")

female_plt = make_subplot(df_female, "(B) Average Age of Suicide, Females, 2021")

pdf("/FILEPATH/average_age_of_death_males.pdf", width=14, height=8)
male_plt
dev.off()



pdf("/FILEPATH/average_age_of_death_females.pdf", width=14, height=8)
female_plt
dev.off()



