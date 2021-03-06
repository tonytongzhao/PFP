# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 16:00:35 2014

@author: lenovo
"""

"""
Created on Wed Sep 24 13:37:47 2014

@author: lenovo
"""
import numpy as np
import sys
from numpy import mat,array

def sample(rating,userset,itemset,u_matrix,i_matrix):
    #print np.round(np.random.rand()*len(userset.keys()))
    sampled_u=array(userset.keys())[int(np.random.rand()*len(userset.keys()))]
   # print array(rating[sampled_u].keys())    
    sampled_i=array(rating[sampled_u].keys())[int(np.random.rand()*len(rating[sampled_u].keys()))]
    randperm=np.random.permutation(array(itemset.keys()))    
    for tj in range(len(randperm)):
        sampled_j=randperm[tj]
        if voilate(rating,sampled_u,sampled_i,sampled_j,u_matrix,i_matrix):
            break
    return (sampled_u, sampled_i, sampled_j, tj)

def voilate(rating,sampled_u,sampled_i,sampled_j,u_matrix,i_matrix):
    r=0    
    for i in rating[sampled_u].keys():
        r+=i_matrix[i]*(u_matrix[sampled_u])*((i_matrix[sampled_j]-i_matrix[sampled_i]).T)/len(rating[sampled_u].keys())
    if (1+r)>0:
        return True
    else:
        return False
    
  #  print sampled_i
    return (sampled_u,sampled_i,sampled_j)
    
def update(rating, u_matrix, i_matrix, i, j,eta, delta, rank, r, N_u, N_i):
    #print u
    g=0
    for rr in range((int)((i_matrix.shape[0]-1)/(r+1))):
       g+=rank[rr]
       
    for t_i in rating.keys():
        i_matrix[i]+=eta*(g*i_matrix[t_i]*(u_matrix)/len(rating.keys())+delta*i_matrix[i])
        i_matrix[j]+=eta*(-g*i_matrix[t_i]*(u_matrix)/len(rating.keys())+delta*i_matrix[j])        
    
    u_matrix+=eta*(g*i_matrix[t_i]*((i_matrix[j]-i_matrix[i]).T)/len(rating.keys())+delta*u_matrix)
    norm_f(u_matrix, i_matrix[i],i_matrix[j], N_u, N_i)
    
def norm_f(u_matrix,i_matrix,i_matrix1,N_u,N_i):
    if np.sum(np.square(u_matrix)) > N_u:
	    u_matrix*=N_u/np.sum(np.square(u_matrix))
    if np.sum(np.square(i_matrix)) > N_i:
	    i_matrix*=N_i/np.sum(np.square(i_matrix))
    if np.sum(np.square(i_matrix1)) > N_u:
	    i_matrix1*=N_u/np.sum(np.square(i_matrix1))
 
def cal_idcg(n):
    idcg=0
    for i in range(n):
        idcg+=1/(np.log(i+2)/np.log(2))
    return (idcg)


def evaluate(rating, testing, u_matrix, i_matrix):
    cumu_auc=0    
    num_t_u=0
    cumu_ndcg=0
    for u in testing.keys():                 
        tmp_u1=mat(np.zeros((1,i_matrix.shape[1])))
        for i in rating[u].keys():
            tmp_u1+=i_matrix[i]  
        tmp_u=tmp_u1*(u_matrix[u])*(i_matrix.T)

        eval_u={}
        #print i_matrix.shape[0]
        for i in range(i_matrix.shape[0]):
            if i not in rating[u].keys():
                eval_u[i]=tmp_u[0,i]
        ranked_u=sorted(eval_u.items(), key = lambda x:x[1], reverse=True)       
       # print ranked_u        
        hit=0
        idcg=cal_idcg(len(testing[u].keys()))
        dcg=0
        num_correct_pairs=0        
        for i in range(len(ranked_u)):
         
            if ranked_u[i][0] in testing[u].keys():
                hit+=1
                dcg+=1/(np.log(i+2)/np.log(2))
            else:
                num_correct_pairs+=hit
        cumu_auc+= (float)(num_correct_pairs)/((len(eval_u.keys()) - len(testing[u].keys())) * len(testing[u].keys()))        
        cumu_ndcg+=dcg/idcg
        num_t_u+=1    
    print cumu_auc
    print num_t_u
    return (cumu_auc/num_t_u, cumu_ndcg/num_t_u)
    
def pfp_warp_avg(d_path,d_trfile,d_tefile,output,num_k,eta,delta,num_iter, N_u, N_i) :  
#    d_path=argv[1]
#    d_trfile=argv[2]
#    d_tefile=argv[3]
#    num_k=argv[4]
#    eta=argv[5]
#    delta=argv[6]    
#    num_iter=argv[7]
#          
    num_iter=(int)(num_iter)
    delta=(float)(delta)
    eta=(float)(eta)
    num_k=(int)(num_k)      
    N_u=(float)(N_u)
    N_i=(float)(N_i)
    rating = {}
    testing= {}
    
    
    userset= {}
    itemset= {}

    max_user=0
    max_item=0
   
       
   
    with open(d_path+d_trfile, 'r') as f:
        for line in f:
            lstr = line.strip().split()
            u, i, r = [float(k) for k in lstr]
            rating[u] = rating.get(u,dict())
            rating[u][i] = r
            userset[u]=userset.get(u,int())
            itemset[i]=itemset.get(i,int())
            userset[u]=u
            itemset[i]=i
            if max_user<u:
                max_user=u
            if max_item<i:
                max_item=i
                
    print max_user
    print max_item
    with open(d_path+d_tefile, 'r') as f:
        for line in f:
            lstr = line.strip().split()
            u, i, r = [float(k) for k in lstr]
            testing[u] = testing.get(u,dict())
            testing[u][i] = r
    print "Initializing..."
    u_matrix={}
    for u in rating.keys():
        u_matrix[u]=u_matrix.get(u,mat(np.random.rand(num_k,num_k)))
        
    i_matrix=mat(np.random.rand(max_item+1,num_k))

    rank=[(i_matrix.shape[0]-i)/i_matrix.shape[0] for i in range(i_matrix.shape[0])]    
    
    print "Begin training..."
    for iter in range(num_iter):
        [u,i,j,r]=sample(rating,userset,itemset,u_matrix,i_matrix)
       # print [u,i,j]
        update(rating[u],u_matrix[u],i_matrix,i,j,eta,delta,rank,r,N_u, N_i)
    print "Evaluating..."
    [e,ndcg]=evaluate(rating, testing,u_matrix,i_matrix)
    print e
    print ndcg
    with open(output, 'w+') as f1:
	    f1.write('%s\t' %(d_path))
	    f1.write('num_k: %d\t' %(num_k))
	    f1.write('eta: %f\t' %(eta))
	    f1.write('auc: %f\t' %(e))
	    f1.write('NDCG: %f\n' %(ndcg))
if len(sys.argv) !=11:
    print "Help\npython pfp.py data_path train_file test_file output_file num_latent_factor learning_rate regularization_term num_iter user_norm item_norm\n"        

d_path=sys.argv[1]
d_trfile=sys.argv[2]
d_tefile=sys.argv[3]
output=sys.argv[4]
num_k=sys.argv[5]
eta=sys.argv[6]
delta=sys.argv[7]
num_iter=sys.argv[8] 
N_u=sys.argv[9]
N_i=sys.argv[10]
print num_k
print eta   
print output
pfp_warp_avg(d_path,d_trfile,d_tefile,output,num_k,eta,delta,num_iter, N_u, N_i)   
