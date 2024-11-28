# %%
import pandas as pd 
import networkx as nx
import matplotlib.pyplot as plt
import getopt, sys

# USAGE
#
# python CLI-max-ind-set.py -r <relatedness_file> -n <novelty_file> -q <quality_file>
#
# - the relatedness file is the output from KING (king.kin0)
# - the novelty file must have a column named 'ID' and 'novelty', where novelty is an integer value
# - the quality file must have a column named 'ID' and 'quality', where the quality is an integer value
#   (note that for quality, a higher value is higher quality)
#


# %%
# ----------------------------------------------------------
# Function: create a table of nodes involved in first degree
# relationships. Annotate with degrees of first and second degree
# relationship by node (sample)
# Parameters : two graphs, one with first degree relationships, 
#               one with second degree relationships
# Output : returns a dataframe with nodes from the first degree graph
#          with additional columns showing how many first and how many
#          second degree relationships it has.
#------------------------------------------------------------
def create_node_table(G1, G2):
  first_list = G1.nodes()

  # Extract node degrees as a list of tuples
  node_first_degrees = [(node, degree) for node, degree in G1.degree()]

  # Create a Pandas DataFrame
  df = pd.DataFrame(node_first_degrees, columns=['ID', 'Degree_1'])

  # Method to extract degree from another graph (default 0 if not found in graph)
  def get_degree_2(node, Gr):
      if node in Gr.nodes():
          return Gr.degree(node)
      else:
          return 0
      
  #Add a new column 'Degree_2' showing its degree of second degree relationships
  df['Degree_2'] = df['ID'].apply(lambda node: get_degree_2(node, G2))

  return df




# %%
# --------------------------------------
# Function: calculate the maximal independent set from a ranked table
#           using a greedy algorithm.
#
# Parameters: 
#           ranked_df: the ranked dataframe, with a column 'ID' with 
#                      sample IDS
#           G : the graph with first-degree relationships. There should be 
#               a 100% overlap between the 'ID' column in ranked_df and the
#               nodes in this graph
#-----------------------------------------
def maximal_independent_set_ranked(ranked_df, G):
    I = []
    Gd = G.copy() # create a copy of the first degree graph
    rank_cp = ranked_df.copy()

    
    while (not nx.is_empty(Gd)):
        nextID = rank_cp['ID'].iloc[0]
        #add top ranked node to independent set,
        I.append(nextID)


        #remove it, and all neighbors from graph and ranked list

        neighbors = Gd.neighbors(nextID)

        #create list from iterator
        neighbor_list = []
        for neigh in neighbors:
            neighbor_list.append(neigh)

        #remove neighbor from graph or list if it is in the neighbor list
        for neigh in neighbor_list:
            Gd.remove_node(neigh)
            rank_cp.drop(rank_cp[rank_cp['ID'] == neigh].index, inplace = True)
            rank_cp = rank_cp.reset_index(drop=True)
        
        #remove node itself 
        Gd.remove_node(nextID)
        rank_cp = rank_cp.drop(index=0)
        rank_cp = rank_cp.reset_index(drop=True)

    #return the independent set
    return I



# %%
#-----------------------------------------------------------------------------------
#test independence
# the nodes in the independent set, when paired, should not have any edges in the 
# graph for first degree relationships
#-----------------------------------------------------------------------------------

def test_independence(ind_list, G):
    #create a "potential adjacency list" size n*(n-1)/2
    # where n is the size of ind_list, in the case where
    # the graph is complete
    is_independent = False #set flag as false by default

    con_G = nx.complete_graph(ind_list)

    set1 = set(con_G.edges())
    set2 = set(G.edges())
    
    if (len(set1.intersection(set2)) == 0) :
        is_independent = True

    return is_independent

#--------------------------------------------------------
#     MAIN
#--------------------------------------------------------

def main():
    #-------------
    # CLI OPTIONS
    #-------------------

    #flags to be set by optional args
    qual_opt = False
    novelty_opt = False
    required = False

    # Remove 1st argument from the
    # list of command line arguments
    argumentList = sys.argv[1:]

    # Options
    options = "hq:n:d:r:"

    try:
        # Parsing argument
        opts, args = getopt.getopt(argumentList, options)
        
        for opt, arg in opts:

            if opt in ("-h"):
                print("""
 ------- USAGE----------------------

 python CLI-max-ind-set.py -r <relatedness_file> -n <novelty_file> -q <quality_file>

 - required parameter: -r <relatedness_file>
 - optional parameters: -n <novelty_file> -q <quality file>
                      
The priority of selecting the next node is:
                      (1) lowest degree for first degree relationships
                      (2) lowest degree for second degree relationships
                      (3) highest novelty (if option used)
                      (4) highest quality (if option used)
                      
 - the relatedness file is the output from KING (king.kin0)
 - the novelty file must have a column named 'ID' and 'novelty', where novelty is an integer value
 - the quality file must have a column named 'ID' and 'quality', where the quality is an integer value
   (note that for quality, a higher value is higher quality)                                                                                

""")
                sys.exit()
                
            if opt in ("-q"):
                print ("Using quality ranking")
                qual_tsv=arg
                qual_opt = True

            if opt in ("-n"):
                print ("Using novelty ranking")
                novel_tsv=arg
                novelty_opt = True
                
            if opt in ("-r"):
                print ("Relationship file: " + str(arg))
                rel_tsv=arg
                required = True
            
                
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        sys.exit()

    if (not required):
        raise Exception("option -r is required with a relationship file (KING output)")
        sys.exit()

    # %%
    #---------------------------------------------------
    # Import data, build, and plot relationship graph
    # ---------------------------------------------------
    rel_df = pd.read_table(rel_tsv)
    rel_df['ID1'] = rel_df['ID1'].astype(str)
    rel_df['ID2'] = rel_df['ID2'].astype(str)
    rel_df['InfType'] = rel_df['InfType'].astype(str)

    #extract first and second degree dataframes and define edge lists
    rels_deg1 = ['PO', 'FS', 'Dup/MZ'] 
    rel_df_1 = rel_df.loc[rel_df['InfType'].isin(rels_deg1)] 
    rel_df_2 = rel_df[rel_df['InfType'] == '2nd'] 

    rel_list_1 = list(zip(rel_df_1['ID1'], rel_df_1['ID2']))
    rel_list_2 = list(zip(rel_df_2['ID1'], rel_df_2['ID2']))

    #create first and second degree relationship graphs
    G1 = nx.Graph()  #graph of first degree relationships
    G2 = nx.Graph()  #graph of second degree relationships

    G1.add_edges_from(rel_list_1)
    G2.add_edges_from(rel_list_2)


    # %%
    #create node table for ranking nodes with first degree relationships
    node_df = create_node_table(G1,G2)

    # %%
    #get annotation tables and then add to node table
    if (qual_opt):
        quality_df = pd.read_table(qual_tsv, sep=' ')
        node_df = node_df.merge(quality_df, on='ID')

    if (novelty_opt):
        novelty_df = pd.read_table(novel_tsv, sep=' ')
        node_df = node_df.merge(novelty_df, on='ID')
 
    
    # %%
    #-------------------------------------------------------------
    #sort the dataframe, thereby creating the priority ranking for
    # keeping nodes in the maximal independent set
    # Rank, in order, by:
    # - lowest number of first degree relationships
    # - lowest number of second degree relationships
    # - number of novel variants
    # - highest quality value
    #--------------------------------------------------------------
    
#sort depending on option
    if (qual_opt and novelty_opt):
        node_df = node_df.sort_values(by=['Degree_1', 'Degree_2', 'novelty', 'quality'], 
                    ascending=[True, True, False, False])
    elif (qual_opt):
        node_df = node_df.sort_values(by=['Degree_1', 'Degree_2', 'quality'], 
                    ascending=[True, True, False])
    elif (novelty_opt):
        node_df = node_df.sort_values(by=['Degree_1', 'Degree_2', 'novelty'], 
                    ascending=[True, True, False])
    else:
        node_df = node_df.sort_values(by=['Degree_1', 'Degree_2'], 
                    ascending=[True, True])

    #fix df indices after ranking
    node_df = node_df.reset_index(drop=True)


    # %%
    #calculate independent set and its complement
    ind = maximal_independent_set_ranked(node_df, G1)
    filter_list = list(set(G1.nodes) - set(ind))



    # ------------------------------------
    # Write information, tsv files, and plots
    #--------------------------------------

    print("\n---------------------")
    print("Ranking Table:")
    print("---------------------")
    print(node_df)


    # %%
    print("\n\nTest independence result: " + str(test_independence(ind, G1)))

    # %%
    #write graph information to file
    with open('./graph_info', mode='wt', encoding='utf-8') as myfile:
        myfile.write('Number of nodes (samples) in 1st degree graph: ' + str(G1.number_of_nodes()) + '\n')
        myfile.write('\nNumber of first degree relationships (edges): ' + str(G1.number_of_edges()) + '\n')
        myfile.write('\nNumber of samples in maximal independent set: ' + str(len(ind)) + '\n')
        myfile.write('\nNumber of samples being filtered: ' + str(len(filter_list)) + '\n')
    
    #Provide total nodes list
    with open('./all_samples_list.tsv', mode='wt', encoding='utf-8') as myfile:
        myfile.write('\n'.join(list(set(G1.nodes))))

    #write independent set to file
    with open('./max_ind_set.tsv', mode='wt', encoding='utf-8') as myfile:
        myfile.write('\n'.join(ind))

    #write samples to filter to file
    with open('./rel_samples_to_filter.tsv', mode='wt', encoding='utf-8') as myfile:
        myfile.write('\n'.join(filter_list))

    # %%
    # -----------------------------------------------
    # Plot Figures
    #------------------------------------------------

    print(f"Maximal Independent set: {ind}")

    fig2 = plt.figure(figsize=(96,72), dpi=120)

    pos = nx.spring_layout(G1, seed=39299899)

    #red for filtered, blue for keeping
    nx.draw(
        G1,
        pos=pos,
        with_labels=True,
        node_color=["tab:red" if n in filter_list else "tab:blue" for n in G1],
        ax=fig2.add_subplot()
    )

    fig2.savefig("max_ind_graph.png")   # Save plot to file


#-------------------------------------------------
if __name__ == "__main__":
    main()

