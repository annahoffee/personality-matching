
###### what percent of ppl that met a speed dater liked vs. didn't like them ( the speed dater)
results <- read.table("output1.txt")
results <- as.matrix(results)
## find the percentage of people that
indices <- which(grepl("/", results))

#/(results[x+1,]+ results[x+2, ])
percent_of_not_fans <- sapply(indices, function(x)as.numeric(results[x+2,])/(as.numeric(results[x+1,]) + as.numeric(results[x+1, ])))

pdf("histogram_percent_of_not_fans.pdf", main="Percent of 'Dislikes' that People Recieve", xlab="Percent")
hist(percent_of_not_fans)
dev.off()


######## look at distributions of ratings for people that got liked vs. disliked

f <- read.csv("speed_dating_data.csv", header=TRUE)
distinct.iids <- unique(f["iid"])
like.ratings <- vector()
dislike.ratings <- vector()
for( iid in as.vector(unlist(distinct.iids))){
  indices <- which(f["iid"] == iid)
  index.like <- which(f[indices, "dec"] == 1)
  index.dislike <- which(f[indices, "dec"] == 0)

  like.ratings <- c(like.ratings, f[indices, "like"][index.like])
  dislike.ratings <- c(dislike.ratings, f[indices, "like"][index.dislike])

}

t <- seq(0, 10, .5)
pdf("histogram_ratings_of_liked_people.pdf")
plot(t, dnorm(t, 6.5, 1.3), main="Distribution of Ratings of 'Liked' People",  xlab="Ratings", ylab="Frequency", type="l", lwd=4, col="#6812dd" ,  yaxt="n")
par(new=TRUE)
hist(like.ratings, main=NULL,  xlab=NULL, ylab=NULL, xaxt="n")
dev.off()

pdf("histogram_ratings_of_disliked_people.pdf")
plot(t, dnorm(t, 5, 2), main="Distribution of Ratings of 'Disliked' People",  xlab="Ratings", ylab="Frequency", type="l", lwd=4, col="#6812dd" ,  yaxt="n")
par(new=TRUE)
hist(dislike.ratings, main=NULL,  xlab=NULL, ylab=NULL, xaxt="n")

dev.off()


#### now do the same thing but instead of ratings use correlation of interests

f <- read.csv("speed_dating_data.csv", header=TRUE)
distinct.iids <- unique(f["iid"])
like.corr <- vector()
dislike.corr <- vector()
for( iid in as.vector(unlist(distinct.iids))){
  indices <- which(f["iid"] == iid)
  index.like <- which(f[indices, "dec"] == 1)
  index.dislike <- which(f[indices, "dec"] == 0)

  like.corr <- c(like.corr, f[indices, "int_corr"][index.like])
  dislike.corr <- c(dislike.corr, f[indices, "int_corr"][index.dislike])

}


t <- seq(-0.83, .78, .05)
pdf("histogram_correlation_of_liked_people.pdf")
hist(like.corr, main="Corrlation of Interest Variables of 'Liked' People", xlab="Correlation Coefficient", ylab="Frequency", xaxt="n")
axis(1, at=seq(min(like.corr, na.rm=TRUE), max(like.corr, na.rm=TRUE), .1 ) )
par(new=TRUE)
plot(t, dnorm(t, .12, .3), type="l", lwd=3, col="#6812dd", xaxt="n", yaxt="n")
dev.off()

t <- seq(-0.83, .78, .05)
pdf("histogram_correlation_of_disliked_people.pdf")
hist(dislike.corr, main="Corrlation of Interest Variables of 'Disliked' People", xlab="Correlation Coefficient", ylab="Frequency", xaxt="n")
axis(1, at=seq(min(like.corr, na.rm=TRUE), max(like.corr, na.rm=TRUE), .1 ) )
par(new=TRUE)
plot(t, dnorm(t, .09, .3), type="l", lwd=3, col="#6812dd", xaxt="n", yaxt="n")

dev.off()


########## what percentage of likes vs. dislikes do people get ###########

f <- readLines("output_test2.txt")

fans.indices <- which(f == "fans")
fans.indices <-  fans.indices + 1

fans.number <- as.numeric(f[fans.indices])

not.fans.indices <- which(f == "not fans")
not.fans.indices <- not.fans.indices + 1

not.fans.number <- as.numeric(f[not.fans.indices])

fans.percentage <- vector()
not.fans.percentage <- vector()

for( x in seq(1, length(not.fans.number), 1)){

  a <- fans.number[x]/(not.fans.number[x] + fans.number[x])
  b <-  not.fans.number[x]/(not.fans.number[x] + fans.number[x])
  fans.percentage <- c(fans.percentage, a )
  not.fans.percentage <- c(not.fans.percentage, b)

}

t <- seq(0, 1.05, .05)
pdf("not_fans_percentage.pdf")
hist(not.fans.percentage, main="Percentage of 'Dislikes' That People Get", xlab="Fraction", ylab="Frequency")
par(new=TRUE)
plot(t, dnorm(t, .6, 3 ), xlab="", ylab="", main=NULL, xaxt="n", yaxt="n", type="l", lwd=3, col="#c8192e")
dev.off()


t <- seq(-0.05, 1.05, .05)
pdf("fans_percentage.pdf")
hist(fans.percentage, main="Percentage of 'Likes' That People Get", xlab="Fraction", ylab="Frequency")
par(new=TRUE)
plot(t, dnorm(t, .3, .5 ), xlab="", ylab="", main=NULL, xaxt="n", yaxt="n", type="l", lwd=3, col="#c8192e")
dev.off()


#############  get all the input person trait vectors ######################

f <- readLines("output_test2.txt")

age.indices <- which(grepl("age", f))
other.indices <- which(grepl("other", f))
input.people <- vector(mode="list")

for( x in seq(length(age.indices))){

  lst <- as.numeric(substr(f[age.indices[x]:other.indices[x]], 19, 21))
  input.people[[x]] <- lst

}



############# trait variance of people that liked person x and people that disliked person x ####################



f <- readLines("output_test2.txt")

fans.indices <- which(f == "fans")
fans.indices <-  fans.indices + 1

fans.number <- as.numeric(f[fans.indices])

not.fans.indices <- which(f == "not fans")
not.fans.indices <- not.fans.indices + 1

not.fans.number <- as.numeric(f[not.fans.indices])

fans.percentage <- vector()
not.fans.percentage <- vector()


fans.indices <- fans.indices + 2   ## the line numbers of the first fan vectors
not.fans.indices <- not.fans.indices + 1  ## the line numbers of the first not fan vectors

convertString <- function(string){
    categorical <- substr(string, 3, 21 )
    numeric <- substr(string, 26,  110)
    traits <- paste0(categorical, numeric)
    traits <- as.numeric(unlist(strsplit(traits, ",")))

    return(traits)


}

fan.list <- vector(mode="list")
not.fan.list <- vector(mode="list")

fan.list.simple <- vector(mode="list")
not.fan.list.simple <- vector(mode="list")


for( x in seq(1, length(not.fans.number), 1)){
    print(x)
    if(fans.number[x] == 0 | not.fans.number[x] == 0 | x == 243){next}
    fans.row.numbers <- seq(fans.indices[x] +1, fans.indices[x] + fans.number[x], 1)
    not.fans.row.numbers <- seq(not.fans.indices[x],  not.fans.indices[x] + not.fans.number[x] -1, 1)

    fan.vectors <- f[fans.row.numbers]
    fan.mat <- matrix(nrow=length(fans.row.numbers), ncol=23)

    for(y in seq(length(fan.vectors))){

         if( length(convertString(fan.vectors[y])) != 23 ){

              fan.mat[y, ]<- rep(NA, 23)
         }else{
              fan.mat[y, ]<- convertString(fan.vectors[y])
         }

    }

    fan.list.simple[[x]] <- fan.mat
    fan.list[[x]] <- apply(fan.mat, 2, var, na.rm=TRUE)

    not.fan.vectors <- f[not.fans.row.numbers]
    not.fan.mat <- matrix(nrow=length(not.fans.row.numbers), ncol=23)
    for(z in seq(length(not.fan.vectors))){

         if( length(convertString(not.fan.vectors[z])) != 23 ){

              not.fan.mat[z, ]<- rep(NA, 23)
         }else{
            not.fan.mat[z, ]<- convertString(not.fan.vectors[z])
         }

    }
    not.fan.list.simple[[x]] <- not.fan.mat
    not.fan.list[[x]] <- apply(not.fan.mat, 2, var, na.rm=TRUE)

}
######## plot fan list stuff #########

k <- 511
 l = c( "age", "gender",  "field", "career", "go_out", "sports", "tvsports", "exercise", "dining", "art", "camping", "gaming", "clubbing", "reading", "movies", "concerts", "music", "yoga", "black", "white", "latino", "asian", "native_A", "other" )
pdf("variance_person511.pdf")
plot(not.fan.list[[k]], type="l", lwd=2, xlab=NULL, col="black", xaxt="n", ylab="Variance", main="Variance for each Trait Variable")
axis(1, at=seq(1, 24, 1 ), labels=l, las=2)
par(new=TRUE)
plot(fan.list[[k]], type="l", yaxt="n", xaxt="n", col="red", ylab="", xlab="", lwd=2)
legend("topright", c("Liked Person #511", "Didn't Like Person #511"), col=c("red", "black"), lty=1)
dev.off()


############ plot simple fan list stuff ######################

k <- 467
order <- c(8, 1 ,9, 10, 11, 12, 13, 14,15,16,17,18,19,20,21,22, 23, 24, 2,3,4,5,6,7)
m <- fan.list.simple[[k]]
m2 <- not.fan.list.simple[[k]]
l = c( "age", "gender",  "field", "career", "go_out", "sports", "tvsports", "exercise", "dining", "art", "camping", "gaming", "clubbing", "reading", "movies", "concerts", "music", "yoga", "black", "white", "latino", "asian", "native_A", "other" )
pdf("person467_simple.pdf")
plot(input.people[[k]], type="l", col="black", lwd=3, main="Variable Values", xaxt="n")
  par(new=TRUE)
axis(1, at=seq(1, 24, 1 ), labels=l, las=2)
vec <- rep(0,length(l))
for(h in seq(nrow(m))){
    vec <- rowMeans(cbind(vec, fan.list.simple[[k]][h, ][order]), na.rm=TRUE)
  }

  vec <- vec/length(nrow(m))

  lines(vec, col="red" , xaxt="n", yaxt="n", main=NULL, xlab="", ylab="")
  #par(new=TRUE)
  vec2 <- rep(0, length(l))
  for(h in seq(nrow(m2))){
    vec2 <- rowMeans(cbind(vec2, not.fan.list.simple[[k]][h, ][order]), na.rm=TRUE)
  }
  vec2 <- vec2/length(nrow(m2))
  lines( vec2, col="blue", xaxt="n", yaxt="n", main=NULL, xlab="", ylab="")

legend("topright", c("Liked Person #467", "Didn't Like Person #467"), col=c("red", "blue"), lty=1)
dev.off()



########## now find average variances

average.fan.variance <- vector()
average.not.fan.variance <-vector()

for( x in seq(1, length(not.fan.list), 1)){

   #not.fan.list[[x]][which(not.fan.list[[x]] > 50 )] <- NA
   not.fan.list[[x]][which(not.fan.list[[x]] == max(not.fan.list[[x]] , na.rm=TRUE))] <- NA
   not.fan.list[[x]][which(not.fan.list[[x]] == max(not.fan.list[[x]] , na.rm=TRUE))] <- NA
   average.not.fan.variance <- c(average.not.fan.variance, mean(not.fan.list[[x]], na.rm=TRUE))

   #fan.list[[x]][which(fan.list[[x]] > 50 )] <- NA
   fan.list[[x]][which(fan.list[[x]] == max(fan.list[[x]] , na.rm=TRUE))] <- NA
   fan.list[[x]][which(fan.list[[x]] == max(fan.list[[x]] , na.rm=TRUE))] <- NA
   average.fan.variance <- c(average.fan.variance, mean(fan.list[[x]], na.rm=TRUE))

}

t <- seq(0,9,1)
pdf("average_fan_variance.pdf")
hist(average.fan.variance, main="Average Variance of People that 'Liked' the same person", xlab="Variance", ylab="Counts", xaxt="n")
axis(1, at=seq(0,9,1), labels=seq(0,9,1))
par(new=TRUE)
plot(t, dnorm(t, 4.8, 1.5), ylab="", xlab="",cex.main=1.6, main=NULL, lwd=3, xaxt="n", yaxt="n", type="l", col="#1bb919")
dev.off()

t <- seq(0,9,1)
pdf("average_fan_not_variance.pdf")
hist(average.not.fan.variance, main="Average Variance of People that 'Disliked' the same person", xlab="Variance", ylab="Counts", xaxt="n")
axis(1, at=seq(0,9,1), labels=seq(0,9,1))
par(new=TRUE)
plot(t, dnorm(t, 4.7, 1), ylab="", xlab="",cex.main=1.6, main=NULL, lwd=3, xaxt="n", yaxt="n", type="l", col="#1bb919")
dev.off()

hist(average.not.fan.variance)

pdf("testing.pdf")
plot(input.people[[316]], type="l", col="red", lwd=3)
par(new=TRUE)
lines(not.fan.list[[316]], col="blue")
lines(fan.list[[316]])
dev.off()



############## more stuff #############

not.fan.counts <-  rep(0, length(not.fan.list))
fan.counts <-  rep(0, length(fan.list))

for(x in seq(length(not.fan.list))){

  not.fan.counts[[x]] <- not.fan.counts[[x]] + length(which(not.fan.list[[x]][8:24] < 1))
  fan.counts[[x]] <- fan.counts[[x]] + length(which(fan.list[[x]][8:24] < 1))

     }
