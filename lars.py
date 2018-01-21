import csv
import scipy as SP
import scipy.linalg as LA
import scipy.stats as ST
import scipy.optimize as OPT
import sklearn.linear_model as LM

## Main program

n_s = 4754
y = SP.array(list(csv.reader(open('pheno','rb'),
                             delimiter='\t'))).astype(float)
y = y[:4754,:]
y = y[:,2].reshape((n_s,1))#feature 3


# load genotypes
X = SP.array(list(csv.reader(open('geno','rb'),delimiter='\t'))).astype(float)

# remove snp label
X = X[:,:n_s]
n_f = X.shape[0]
for i in xrange(n_f):
    sd=(X[i]).std()
    if sd == 0:
        X[i]=X[i]-(X[i]).mean()
    else:
        X[i]=(X[i]-(X[i]).mean())/sd
X = X.T
print X
print X.shape

parents = SP.array(list(csv.reader(open('parents.txt','rb'),
                                   delimiter='\t'))).astype(int)
parents=parents[:4754,:]
idxm=range(1,191)
SP.random.shuffle(idxm)
idxm=idxm[:5]
idxf=range(1, 26)
SP.random.shuffle(idxf)
idxf=idxf[:5]

train=[]
test1=[]
test2=[]
for i in xrange(n_s):
    if parents[i,1] in idxf:
        test2=test2+[i]
    else:
        if parents[i,0] in idxm:
            test1=test1+[i]
        else:
            train=train+[i]
train2=train+test1
test=test1+test2

yhat=SP.zeros((n_s,1))
yhat[train]=y[train]

def train_and_eval_with_select(Xtrain,Xtest,ytrain):
    ytrain=ytrain.ravel()
    from sklearn.feature_selection import f_regression
    F, p=f_regression(Xtrain,ytrain)
    features=[]
    for i in xrange(Xtrain.shape[1]):
        if p[i]<0.001:
            print p[i]
            features+=[i]
    print len(features)
    Xtrain=Xtrain[:,features]
    Xtest=Xtest[:,features]
    reg=LM.BayesianRidge(n_iter=30)
    reg.fit(Xtrain, ytrain)
    res=reg.predict(Xtest)
    return res.reshape((res.shape[0],1))

def train_and_eval(Xtrain,Xtest,ytrain):
    ytrain=ytrain.ravel()
    reg=LM.BayesianRidge(n_iter=100)
    reg.fit(Xtrain, ytrain)
    res=reg.predict(Xtest)
    return res.reshape((res.shape[0],1))


yhat[test1]=train_and_eval(X[train], X[test1], yhat[train])
yhat[test2]=train_and_eval(X[train2], X[test2], yhat[train2])


print yhat[test].ravel()
corr = 1./len(test) * SP.dot((yhat[test]-yhat[test].mean()).T,y[test]
                             -y[test].mean())/(yhat[test].std()*y[test].std())
print corr[0,0]
