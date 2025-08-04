from django.dispatch import Signal

# signal provides these params: # sender: Type[LoggingCommand], log_instance: Log, service_name:str, status:LogStatus,
logging_command_completed = Signal()
