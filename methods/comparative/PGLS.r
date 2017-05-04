## two possible high-level uses  ( note that through rpy2 dots in function names become underscores )
# out <-  FUN.CUSTOM.pgls(x, y, tree, model)      ## where model =   "Null", "BM","lambda", "OU"
# out <- FUN.CUSTOM.pgls.full(x, y, tree)         ## i.e. run all models

# minimal siming analysis on two traits; ordinary and generalized regression analysis with multiple variance-covariance matrices, 
# reflecting various models for the residuals to be dependent on the input tree
library("ape")
#library("annotate")
#library("Biobase")
#library("phytools")
#require("phylolm")
#require("nlme")
#require("PIGShift")
#require("Biobase")

####################################################### DEFINITIONS

#####  modify tree to keep only leaves in a list ############################
#; should not be useful if data provided already matches the criterion
FUN.droptip = function(tree, names.keep) {
  ### a function to remove tips of phylogenetic tree.
  ### drop names that are not in names.keep
  if (!all(tree$tip.label %in% names.keep)) 
  {  tree = drop.tip(phy=tree, tip=tree$tip.label[!(tree$tip.label %in% names.keep)]) }
  return(tree)
}
################################################################################

##### prepare x and y   ########################################################
prepare.xy = function(x.input, y.input, tree.input){ #}, vy.input) {
  
  ### make x and y into matrix
  x.matrix = as.matrix(x.input)
  y.matrix = as.matrix(y.input)
  ### remove NA rows
  x.matrix = as.matrix(x.matrix[complete.cases(x.matrix),])
  y.matrix = as.matrix(y.matrix[complete.cases(y.matrix),])
  #### if vy.input is NULL  ### only case!
  #if (is.null(vy.input)) {
    common.species = intersect(intersect(rownames(x.matrix), rownames(y.matrix)), tree.input$tip.label)
    tree = FUN.droptip(tree.input, common.species)
    species.order = rownames(vcv(tree))
    x.matrix = as.matrix(x.matrix[species.order, ])
    y.matrix = as.matrix(y.matrix[species.order, ])
    return(list(tree=tree, x.matrix=x.matrix, y.matrix=y.matrix)) #, vy.vector=NULL))
  #} else {
  #  vy.vector = vy.input[complete.cases(vy.input)]
  #  common.species = intersect(intersect(intersect(rownames(x.matrix), rownames(y.matrix)), tree.input$tip.label), names(vy.vector))
  #  tree = FUN.droptip(tree.input, common.species)
  #  species.order = rownames(vcv(tree))
  #  x.matrix = as.matrix(x.matrix[species.order, ])
  #  y.matrix = as.matrix(y.matrix[species.order, ])
  #  vy.vector = vy.vector[species.order]
  #  return(list(tree=tree, x.matrix=x.matrix, y.matrix=y.matrix, vy.vector=vy.vector))
  #}
}
################################################################################
##### various ways to compute vcv according to different models   ##############
### vcv by NULL               ##############
vcv.null = function(tree) {
  V = diag(1, length(tree$tip.label))
  rownames(V) = tree$tip.label
  colnames(V) = tree$tip.label
  return(V)
}
### vcv by BM                 ##############
vcv.bm = function(tree) {
  ### vcv of tree
  V = vcv(tree)
  return(V/V[1,1])     #just for consistency with ou
}
### vcv by lambda transform   ##############
vcv.lambda = function(tree, lambda) {
  ### get BM of tree
  C = vcv(tree)
  ### new VCV
  dC = diag(diag(C))
  V = lambda * (C - dC) + dC
  return(V/V[1,1])     #just for consistency with ou
}
### vcv by OU transform
vcv.ou = function(tree, alpha) {
  ### get BM of tree
  C = vcv(tree)
  ### new VCV
  V = (exp(2*alpha*C) - 1) / (exp(2*alpha)-1)
  return(V/V[1,1])    #diagonal can be different from 1 (same values); thus we normalize accordingly
}



################################################################################
### ordinary least square regression ###
########################################
lm.ols = function(x.matrix, y.matrix, simple.output) {
  ### estimates of coefficients
  beta.cap = solve(t(x.matrix) %*% x.matrix) %*% t(x.matrix) %*% y.matrix
  ### residual
  residual = y.matrix - x.matrix %*% beta.cap
  ### residual sum of square
  RSS = as.numeric(t(residual) %*% residual)
  ### number of species
  n = nrow(y.matrix)
  ### number of parameters
  npar = length(beta.cap)
  ### ML estimates
  sigma2.ml = RSS/n
  if (simple.output) {
    ### only enough for lm.logL
    return(list(RSS=RSS, n=n, npar = npar, sigma2.ml=sigma2.ml))
  } else {
    ### degree of freedom
    df = n - npar
    ### OLS estimate of sigma2 (variance of the error term)
    sigma2.ols = RSS / df
    ### variance and se of beta.cap
    var.beta.cap = sigma2.ols * solve(t(x.matrix) %*% x.matrix)
    se.beta.cap = sqrt(diag(var.beta.cap))
    ### statistics
    t.val = beta.cap / se.beta.cap
    p.val = pt(-1*abs(t.val), df)*2
    
    return(list(      x.matrix = x.matrix,      y.matrix = y.matrix,      residual = residual,      RSS = RSS, 
      n = n,      npar = npar,       df = df,       sigma2.ols = sigma2.ols,       sigma2.ml = sigma2.ml,
      estimate = cbind.data.frame(coef=beta.cap, se.coef = se.beta.cap, t.val=t.val, p.val=p.val)    ))
  }
}

###########################################
### generalized least square regression ###
### do this via transformation into ols ###
###########################################
lm.gls = function(x.matrix, y.matrix, vcv.matrix = NULL, simple.output) {
  ### transform the input x.matrix and y.matrix using vcv.matrix
  transform.xy.by.vcv = function(x.matrix, y.matrix, vcv.matrix) {
    invV = solve(vcv.matrix)
    invS.matrix = chol(invV)
    x.matrix = invS.matrix %*% x.matrix
    y.matrix = invS.matrix %*% y.matrix
    return(list(x.matrix=x.matrix, y.matrix=y.matrix))
  }
  
  ### give diagonal if needed
  if (is.null(vcv.matrix)) { vcv.matrix = diag(1, nrow(y.matrix))  }
  
  temp =  transform.xy.by.vcv(x.matrix, y.matrix, vcv.matrix)
  c(list(vcv.matrix=vcv.matrix), lm.ols(temp$x.matrix, temp$y.matrix, simple.output))
}


################################################################################
#### maximum likelihood; through which we obtain all models just changing the options (see below)
lm.logL = function(x.matrix, y.matrix, vcv.matrix, nest, sig2.ml, simple.output) {
  
  if (is.null(vcv.matrix)) {    vcv.matrix = diag(1, nrow(y.matrix))  }
  
  ### this should also avoid the problem of non-positive definite matrix
  if (simple.output) {
    
    invV = solve(vcv.matrix)
    ### estimates of coefficients
    beta.cap = solve(t(x.matrix) %*% invV %*% x.matrix) %*% t(x.matrix) %*% invV %*% y.matrix
    ### residual sum of square
    RSS = as.numeric(t(y.matrix - x.matrix %*% beta.cap) %*% invV %*% (y.matrix - x.matrix %*% beta.cap))
    ### number of species
    n = nrow(y.matrix)
    if(sig2.ml) {      sigma2.ml = RSS/n  }  ### ML estimates of sigma2
    else {      sigma2.ml = 1 }       ### VCV fully specify the information

    logL = -n/2 * log(2 * pi) - as.numeric(determinant(sigma2.ml*vcv.matrix, logarithm=T)$modulus/2) - RSS/(2*sigma2.ml)
    return(logL)
    
  } else {
    
    temp = lm.gls(x.matrix, y.matrix, vcv.matrix, simple.output)
    n = temp$n
    RSS = temp$RSS
    npar = temp$npar
    
    if(sig2.ml) {   sigma2.ml = temp$sigma2.ml}    ### ML estimates of sigma2
    else {          sigma2.ml = 1             }    ### VCV fully specify the information
    
    logL = -n/2 * log(2 * pi) - as.numeric(determinant(sigma2.ml*vcv.matrix, logarithm=T)$modulus/2) - RSS/(2*sigma2.ml)
    
    ### AIC, BIC
    AIC = -2*logL + 2 * (npar + nest)
    BIC = -2*logL + log(n) * (npar + nest)
    
    return(c(list(
      logLik = c(AIC = AIC, BIC=BIC, logL = logL)),
      temp
    ))
  }
}
################################################################################
################################################################################
### The actual pgls functions under each evolution mode (without se) ######################
############################ null
pgls.null = function(x.matrix, y.matrix, tree) {
  ### just do logL, sig2.ml, complete.output
  return(lm.logL(x.matrix, y.matrix, vcv.null(tree), 1, T, F))
}
############################ bm
pgls.bm = function(x.matrix, y.matrix, tree) {
  ### just do logL, sig2.ml, complete.output
  return(lm.logL(x.matrix, y.matrix, vcv.bm(tree), 1, T, F))
}
############################ lambda
pgls.lambda = function(x.matrix, y.matrix, tree) {
  ### just do logL, sig2.ml, simple.output
  llk.lambda = function(param, x.matrix, y.matrix, tree) {
    return(lm.logL(x.matrix, y.matrix, vcv.lambda(tree, param), 2, T, T))
  }
  ### optimize param
  op =  optim(par=.5, fn = llk.lambda, 
              x.matrix = x.matrix, y.matrix = y.matrix, tree = tree, 
              method="L-BFGS-B", lower=c(1e-8), upper=1, control=list(fnscale=-1))
  return(c(lm.logL(x.matrix, y.matrix, vcv.lambda(tree, op$par), 2, T, F), 
           convergence = op$convergence, estimate.parameter = list(op$par)))
}
############################ ou 
pgls.ou = function(x.matrix, y.matrix, tree) {
  ### just do logL, sig2.ml, simple.output
  llk.ou = function(param, x.matrix, y.matrix, tree) {
    return(lm.logL(x.matrix, y.matrix, vcv.ou(tree, param), 2, T, T))
  }
  ### optimize param
  op =  optim(par=.5, fn = llk.ou, 
              x.matrix = x.matrix, y.matrix = y.matrix, tree = tree, 
              method="L-BFGS-B", lower=c(1e-8), upper=100, control=list(fnscale=-1))
  return(c(lm.logL(x.matrix, y.matrix, vcv.ou(tree, op$par), 2, T, F), 
           convergence = op$convergence, estimate.parameter = list(op$par)))
}
################################################################################


####### MAIN FUNCTION #########################################################
FUN.CUSTOM.pgls = function(x.input, y.input, tree.input, evolution.mode){ #}, vy.input) {
  temp = prepare.xy(x.input, y.input, tree.input) #, vy.input)
  x.matrix = cbind(1, temp$x.matrix)
  y.matrix = temp$y.matrix
  tree = temp$tree
  #vy.vector = temp$vy.vector
  #if (is.null(vy.vector)) {
    switch(evolution.mode,
           Null = pgls.null(x.matrix, y.matrix, tree),
           BM = pgls.bm(x.matrix, y.matrix, tree),
           lambda = pgls.lambda(x.matrix, y.matrix, tree),
           OU = pgls.ou(x.matrix, y.matrix, tree))
  #} else {
  #  switch(evolution.mode,
  #         Null = pgls.null.se(x.matrix, y.matrix, tree, vy.vector),
  #         BM = pgls.bm.se(x.matrix, y.matrix, tree, vy.vector),
  #         lambda = pgls.lambda.se(x.matrix, y.matrix, tree, vy.vector),
  #         OU = pgls.ou.se(x.matrix, y.matrix, tree, vy.vector))
  #}
}
################################################################################
######## RUN ALL AT ONCE FUNCTION                     #########################
FUN.CUSTOM.pgls.full = function(x, y, tree) {
  list(
    Null=FUN.CUSTOM.pgls(x, y, tree, "Null")[c("logLik", "estimate", "sigma2.ols")],
    BM=FUN.CUSTOM.pgls(x, y, tree, "BM")[c("logLik", "estimate", "sigma2.ols")],
    lambda=FUN.CUSTOM.pgls(x, y, tree, "lambda")[c("logLik", "estimate", "sigma2.ols", "convergence", "estimate.parameter")],
    OU=FUN.CUSTOM.pgls(x, y, tree, "OU")[c("logLik", "estimate", "sigma2.ols", "convergence", "estimate.parameter")]
  )
}

# #### Usage of script: Rscript  siming_pgls.R    x_input.tsv  y_input.tsv  tree_input.nw   model  action
# ##   model can be:  "Null", "BM","lambda", "OU"    or    "all"
# ##   action can be:  ...
# args <- commandArgs(trailingOnly=TRUE)
# x.input.file <-    args[1]
# y.input.file <-    args[2]
# tree.input.file <- args[3]
# model           <- args[4] 
# action          <- args[5] # unused
# x.loaded <- read.table(x.input.file, header = T, sep = "\t")
# y.loaded <- read.table(y.input.file, header = T, sep = "\t")
# t.loaded <- read.tree(tree.input.file)
# if ( model %in% c("Null", "BM","lambda", "OU") ){
#  out <-  FUN.CUSTOM.pgls(x, y, tree, model)
#  } else if ( model =="all" ){   out <- FUN.CUSTOM.pgls.full(x.loaded, y.loaded, t.loaded) }
