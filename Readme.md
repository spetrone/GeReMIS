 
 Input:
 
1. (required) The output from KING -relate  (the .kin0 file) (https://www.kingrelatedness.com/)
    - for best results, include inference with second degree relationships
2. (optional) A file ranking samples by novelty (columns "ID" and "novelty"), where I higher count is a better ranking. Novelty, in this case, is calculated as variants the sample contributes to the variant library that do not intersect with gnomad. 
3.  (optional) A file ranking samples by quality (columngs "ID" and "quality") - where a higher score is a better ranking (the absolute scores do not matter, so long as they are relative scores and higher is better).
 


 
 ------- USAGE----------------------------------------------------------------------------

 python CLI-max-ind-set.py -r <relatedness_file> -n <novelty_file> -q <quality_file>

 - required parameter: -r <relatedness_file>
 - optional parameters: -n <novelty_file> -q <quality file>

 -----------------------------------------------------------------------------------------




The priority of selecting the next node is:
                      (1) lowest degree for first degree relationships
                      (2) lowest degree for second degree relationships
                      (3) highest novelty (if option used)
                      (4) highest quality (if option used)
                      
 - the relatedness file is the output from KING (king.kin0)
 - the novelty file must have a column named 'ID' and 'novelty', where novelty is an integer value
 - the quality file must have a column named 'ID' and 'quality', where the quality is an integer value
   (note that for quality, a higher value is higher quality)      
