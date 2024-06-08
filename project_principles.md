I am an amateur. I write open-source projects because I want to gain experience in designing, writing, and maintaing software; With that said I created this document to note down specific standards and principles I set for myself. There is no chance that everything I do is perfect hence making my principles part of the source means that anyone could read it and correct me on any bad habits or "wrong" ideas. 
If you notice anything that could be improved create an issue, thank you!!

These are more of suggestions and are not forced. However, if there was code that ignores any of these principles then a comment should be written above it stating the reason (if any). 

## Tagged Commits
Commits are to be categorised under one of the following formats:

`` [fixed] ((link to issue that was fixed)) (title of issue, or summary) ``
* This does mean that I will need to create issues for every recorded bug. This is not meant for typos or simple mistakes like that, which are to be labelled under [chore].

`` [chore] (description of what was addressed) ``
* Unlike the [fix] tag, this one does not warrant the creation of an issue and is reserved for minor changes such as typos, commented, or for any changes in the structure of the code.

`` [added] (description of what was added) ``
* Pretty self-explanatory, any added code that increases functionality of the software.

`` [removed] (description of what was removed) ``
* Similar to the [added] tag, any removed code should be tagged with [removed] and should have a description of the regression.

`` [misc] (summary) ``
* Anything that does not fall under any of the aforementioned tags should be labbeled as a miscellaneous change with a summary of what was changed.

Examples:
- `[fixed] (#1234) receiving duplicate notifications`
- `[chore] Corrected typo in README.md`
- `[added] Implemented user profile feature`
- `[removed] Deprecated authentication method`
- `[misc] Updated project dependencies`

## Naming Conventions
There is no particular reasoning behind any of these choices, I just think they look nice :p If there is anything that could be improved please do state the reason (if any). The list is ordered from lowest to highest priority, i.e a function argument that is also a class should be written in snake_case.

- **Variables, Functions**: camelCase
- **Private Functions**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Global Variables**: UPPER_SNAKE_CASE (minimize usage if possible)
- **Modules/Namespaces**: lowercase_with_underscores
- **Enums**: UPPER_SNAKE_CASE
- **File Names**: snake_case
- **Function Arguments**: snake_case
- **Method Names**: camelCase
- **Properties/Instance Variables**: snake_case

## Definitions

* Functions should include type hinting and if it has special return types then write a comment under the function explaining them. Example:
	```
	def _extractData(url: str, yt_dlp_args: dict) -> dict:
		"""
		Returns the dictionary returned by yt_dlp on a successful call.
		Return Types:
			on success: dict
			on systematic errors: None
			on random errors: 0
		""" 
	```
	
	If it's a complex function (vague name, arguments, or return types) then follow the following structure to explain it's usage.
	```
	def _extract_data(url: str, yt_dlp_args: dict) -> dict:
	    """
	    Returns the dictionary returned by yt_dlp on a successful call.
	    
	    Parameters:
	        url (str): The URL of the video or playlist.
	        yt_dlp_args (dict): Additional arguments to pass to yt_dlp.
	
	    Returns:
	        dict: Dictionary containing video/playlist information.
	
	    Return Types:
	        - On success: dict
	        - On systematic errors: None
	        - On random errors: 0
	    """ 
	```


* Class definitions should list out its attributes and methods as such:
```
	class MyClass:
	    """
	    This class represents an example.
	
	    Attributes:
	        attr1: Description of attr1.
	        attr2: Description of attr2.
	
	    Methods:
	        method1: Description of method1.
	        method2: Description of method2.
	    """
```

## Error-handling
// Have not yet bothered to implement it. Should probably do so. When tackled I will update this section with the necessary information as I need to research and actually try it before setting anything concrete.

## Instances
By instances I really mean anything that needs to be closed, disconnected, or otherwise terminated at exit. For example an open file. Any script making use of any instance should always have a ``SIGTERM`` signal handler. Every instance needs to be closed appropriately.

## Cross-Platform compatibility
All projects should be compatible across different Operating Systems, whether its on Linux, MacOS, or any other Unix-like system. Windows is optional but highly encouraged, if not then it should be marked as such. This is of course speaking of Desktop-specific OSs.

## Logs
A script making use of a logger should be clearly named (e.g logger.name = \_\_file\_\_) and should not drown the log file with info. Instead long logs should be written with the DEBUG method and be enabled by the user.
