class Student:
    """
    docstring
    """
    def __init__(self,student_id:int,name:str,email:str):
        self.student_id=student_id
        self.name=name
        self.email=email

    def update_name(self, new_name:str):
        """
        docstring
        """
        self.name=new_name
    
    def upd_mail(self,new_email:str):
        """
        docstring
        """
        self.email=new_email