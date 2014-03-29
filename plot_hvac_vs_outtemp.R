#plot_hvac_vs_outtemp.R
#Greg Fiske
#2/17/14
#plots hvac usage vs outdoor temp for entire winter

#set working directory import module
setwd("C:/Data/python_scripts/pi")
rm(list = ls())
library(ggplot2)

#read data table
mydata = read.table("hvac_outtemp_March29_2014.txt", header=T)

#create a subset hvac data greater than 300 watts
mydata.sub <- subset(mydata, mydata$hvac > 300)
WattHours <- (mydata.sub$hvac)/1000
Temperature <- round(mydata.sub$temperature, digits = 1)

#build model and plot it
png("HVAC_vs_Temp_March29_2014.png", width = 1000, height = 800, pointsize = 10)
par(mar = c(5,5,5,3) + 0.1, oma = c(3,3,3,3), mgp = c(3, 1, 0), cex = 1)
ggplot(mydata.sub,aes(Temperature,WattHours))+
  geom_point(color="grey40",size=4)+
  geom_smooth(fill="green",size=1.5)+
  labs(x = "Temperature (F)", y = "kWh")+
  ggtitle(expression(atop("HVAC Usage vs. Outdoor Temperature", atop(italic("Hourly -- winter 2013-14"), ""))))+
  theme(text = element_text(size=28,vjust=2),axis.text.x = element_text(colour="black",size=30,angle=0,hjust=.5,vjust=1,face="plain"),
        axis.text.y = element_text(colour="black",size=30,angle=0,hjust=1,vjust=0,face="plain"),  
        axis.title.x = element_text(colour="black",size=28,angle=0,hjust=.5,vjust=-0.3,face="plain"),
        axis.title.y = element_text(colour="black",size=28,angle=90,hjust=.5,vjust=0.5,face="plain"))

dev.off()

#calculate cost
cost <- (sum(mydata.sub)/1000)*.21
#now project to time of year when hvac was turned off
lm.mod <- lm(hvac~temperature, data = mydata.sub)
lm.pred <- predict(lm.mod, mydata.sub, se.fit = TRUE, interval = "prediction")
mydata.pred <- cbind(mydata.sub, lm.pred)
lm.all <- predict(lm.mod, mydata, se.fit = TRUE, interval = "prediction")
lm.all.pred <- cbind(mydata, lm.all)
#calc total winter cost from modeled numbers
total.cost <- (sum(lm.all.pred$fit.fit)/1000)*.21
#calc the value saved by burning wood
value.saved <- total.cost - cost

#plot the pred vs obs and get the R2
plot(mydata.pred$hvac,mydata.pred$fit.fit)
slm <- summary(lm.mod) 
str(slm) 
slm$r.squared 
