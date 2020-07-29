1. ### Requirement:
Python >= 3.6, Cplex >= 12.8, pygmo==2.1 (we find that pygmo 2.13 has some severe issues that cause the code using MOEAs to crash)

2. ###  The necessity to install Cplex 12.8 and above:
Academic license that can support problems with more than 1000 decisive variables for the ILP methods, and Set up the Python API of CPLEX https://www.ibm.com/support/knowledgecenter/SSSA5P_12.7.1/ilog.odms.cplex.help/CPLEX/GettingStarted/topics/set_up/Python_setup.html

3. ### The necessity to install Pagmo & Pygmo 2.0 and above: 

in anaconda we can install via this command: pip install pygmo==2.1
For the MOEA methods, the link is https://esa.github.io/pagmo2/

###Besides, the input files for the MCTSM problem is from the Nemo Project: https://github.com/jwlin/Nemo

4. ### To reproduce the RQ1:
It requires the 4 python classes to generate the results: 
	(1) RQ1Config1 means the Big-M+ϵ-constraint for the classic bi-criteria problem.
	(2) RQ1Config2 means the Big-M+CWMOIP for the classic bi-criteria problem.
	(3) RQ1Config3 means the OR-relation+ϵ-constraint for the classic bi-criteria problem.
	(4) RQ1Config4 means the OR-relation+CWMOIP for the classic bi-criteria problem.
	(5) RQ1Config1_varBi means the Big-M+ϵ-constraint for the variant bi-criteria problem.
	(6) RQ1Config2_varBi means the Big-M+CWMOIP for the variant bi-criteria problem.
	(7) RQ1Config3_varBi means the OR-relation+ϵ-constraint for the variant bi-criteria problem.
	(8) RQ1Config4_varBi means the OR-relation+CWMOIP for the variant bi-criteria problem.
	
	e.g., the usage: python RQ1Config1.python <projectName>  
	Note that <projectName> can be "flex", "grep", "gzip", "make", "sed". The data for these projects is from the folder "Nemo/subject_programs/" of the project Nemo, which can be downloaded from https://github.com/jwlin/Nemo 

5.  ### To reproduce the RQ2:
Apart from the above classes to generates results, we also need two more classes:
	(1) RQ2_tri_Config2 means the fastest method (Big-M+CWMOIP) for the tri-criteria problem.
	(2) RQ2_tri_Config3 means the slowest method (OR-relation+ϵ-constraint) for the tri-criteria problem.
	
	e.g., the usage: python RQ2_tri_Config2.python <projectName>  <AllowTestSize>
	Note that <projectName> can be "flex", "grep", "gzip", "make", "sed", and <AllowTestSize> can be "0.05", "0.10", "0.15", "0.2".
	
6. ### To reproduce the RQ3:
We apply the following two MOEAs to generate the results for the *relaxed* tri-criteria problem: 
	(1) moea/RQ3_moeaD means the MOEAD algorithm.
	(2) moea/RQ3_nsga2 means the NSGA2 algorithm.
	(3) moea/RQ3_RstComparator means the comparator class to calculate the normalized HV, execution time and their corresponding p-value for the two MOEAs. 
	
	First, generate the results for the two MOEAs. E.g., the usage: python RQ3_moeaD.python <projectName>  <AllowTestSize>
	Note that <projectName> can be "flex", "grep", "gzip", "make", "sed", and <AllowTestSize> can be "0.05", "0.10", "0.15", "0.2".
	
	Second, after the above step, generate the  the normalized HV, execution time and their corresponding p-value for the two MOEAs.
	E.g., the usage: python RQ3_RstComparator.python <projectName>  <AllowTestSize>	
	Note that <projectName> can be "flex", "grep", "gzip", "make", "sed", and <AllowTestSize> can be "0.05", "0.10", "0.15", "0.2".
