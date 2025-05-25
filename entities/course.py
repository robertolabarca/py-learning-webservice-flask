class Course:
    """
    docstring
    """
    def __init__(self,course_id:int,name:str,description:str):
        """
        docstring
        """
        self.course_id=course_id
        self.name=name
        self.description=description

    def upd_name(self,new_name:str):
        """
        docstring
        """
        self.name=new_name

    def upd_description(self,new_description:str):
        """
        docstring
        """
        self.description=new_description