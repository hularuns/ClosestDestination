import time 
        
def function_progress(start_time, end_time, ongoing_time, total_tasks,
                      pred_avg_time = True, pred_total_time = True):
    """ Function progress timer, Requires 
    `ongoing_time=[]
    cumulative_time_total = 0` to be initalised at start of loop.
    
    each loop should have calculations calculated for, wrapped in start_time and end_time using the `time` package, e.g.:
    
    `import time
    def function:
        start_time = time.time()
        
        computer_intensive_process
        
        end_time = time.time()
        
    elapsed_time = end_time-start_time
    ongoing_time.append(elapsed_time)`
    
    Parameters:
        start_time: time.time() at start of loop.
        end_time: time.time() at end of loop.
        ongoing_time: list of times which are appended to each loop.
        total_tasks: length of dictionary, list etc can be retried using len()
        pred_avg_time: If true will print average time of each loop.
        pred_total_Time: If true will print the predicted average time.
        
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