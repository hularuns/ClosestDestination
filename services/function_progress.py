import time 
        
def function_progress(start_time: time, end_time:time , ongoing_time:list, total_tasks:int,
                      pred_avg_time:bool = True, pred_total_time:bool = True):
    """ Function to be used within a function to track ongoing function progress and to print to console average 
    time for completion and total predicted time.
    
    
    Parameters:
    -----------
        start_time: time.time() at start of loop.
        end_time: time.time() at end of loop.
        ongoing_time: list of times which are appended to each loop.
        total_tasks: length of dictionary, list etc can be retried using len()
        pred_avg_time: If true will print average time of each loop.
        pred_total_Time: If true will print the predicted average time.
        
    Example:
    --------
    >>> import time
    >>> ongoing_time=[]
    >>> cumulative_time_total = 0 #to be initalised at start of loop.
    >>> 
    >>> def function():
    >>>     computer_intensive_process
    >>>         start_time = time.time()
    >>>         end_time = time.time()
    >>>    
    >>>     cumulative_progress = function_progress.function_progress(start_time = start_time, end_time = end_time, 
                                                                  ongoing_time = ongoing_time, total_tasks = len(object_interated_over))
    >>>     cumulative_total += cumulative_progress
    >>>     print(f'The process has been running for {round(cumulative_total, 2)} seconds.')
    """
    
    elapsed_time = end_time - start_time
    ongoing_time.append(elapsed_time)


    if len(ongoing_time) > 0:
        average_time = sum(ongoing_time) / len(ongoing_time)
        total_predicted_time = average_time * total_tasks

        if pred_avg_time:
            print(f'Average time for each completion is {round(average_time, 2)} seconds.')
        if pred_total_time:
            print(f'Total predicted time to complete all tasks is {round(total_predicted_time, 2)} seconds.')
    return elapsed_time