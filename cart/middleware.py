class Mymiddleware:
    def __init__(self,get_response):
        self.get_response=get_response
    def __call__(self,request):
        # print("Before view is called") 
        # print("Request Path:", request.path)
        if request.path == '/login':
            print("Login Request")
        elif request.path == '/register':
            print("Register Request")
        elif request.path=='/cart':
            print('cart page request')
        elif request.path=='/logout':
            print('Logout request')
        elif request.path=='/order':
            print("order Request")
        elif request.path=='/order-history/':
            print("Order history Request")
        elif request.path=='/order-success/':
            print('order success Request.')
        elif request.path=="/":
            print("Home page Request")

        response=self.get_response(request)
        print("After view is called") 
        return response