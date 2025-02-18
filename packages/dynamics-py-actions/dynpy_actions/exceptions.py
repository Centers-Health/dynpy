class ActionNotFoundException(Exception):
    def __init__(self, message=""):
        msg = f"""Action not found. {message}"""
        super().__init__(msg)


class TargetNotSpecifiedException(Exception):
    def __init__(self):
        super().__init__(
            "No target specified. For embed type = target, self.target_elem_id needs to be set"
        )


class AsyncConfirmNotDefinedException(Exception):
    def __init__(self):
        super().__init__(
            "async_confirm undefined. Please define async_confirm(self,request) when using async_confirmation."
        )


class ConflictingConfirmationsException(Exception):
    def __init__(self, action):
        super().__init__(
            f"""Cannot have both synchronous and asynchronous confirmations.
            The {action.name} action has both async_confirmation and needs_confirmation set to True.
            The synchronous confirmation message (ie action.confirmation_message)
            will be overridden by the asynchronous confirmation message (ie action.async_confirm(self,request))
            """
        )
