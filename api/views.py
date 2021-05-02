import datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import AssignedOrder,DeliveryPartner, Vehicle, Order
from api.serializers import AssignedOrderSerializer, DeliveryPartnerSerializer, OrderSerializer


class AssignedOrderList(APIView):
    """
    List all code Assigned Orders.
    """

    @staticmethod
    def get(request):
        orders = AssignedOrder.objects.all()
        serializer = AssignedOrderSerializer(orders, many=True)
        return Response(serializer.data)


class GetDeliveryPartner(APIView):
    """
        List all the delivery partners.
    """

    @staticmethod
    def get(request):
        delivery_partner_obj = DeliveryPartner.objects.all()
        serializer = DeliveryPartnerSerializer(delivery_partner_obj, many=True)
        return Response(serializer.data)


class AddDeliveryPartner(APIView):

    @staticmethod
    def post(request):
        vehicle_exist = Vehicle.objects.filter(vehicle_type = request.data['vehicle_type'])
        serializer = DeliveryPartnerSerializer(data=request.data)
        if vehicle_exist is not None:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return  Response({"vehicle_type not found in our database."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Orders(APIView):

    @staticmethod
    def check_per_slot_100kg(data) -> bool:
        now = datetime.datetime.now()
        current_hour = int(now.hour)
        current_min = int(now.minute)
        # current_hour = 6
        # current_min = 2
        if 6 <= current_hour < 9 or (current_hour == 9 and current_min == 0):
            hours_list = [6,9]
        elif 9 <= current_hour < 13 or (current_hour == 13 and current_min == 0):
            hours_list = [9,13]
        elif 16 <= current_hour < 19 or (current_hour == 19 and current_min == 0):
            hours_list = [16,19]
        elif 19 <= current_hour < 23 or (current_hour == 23 and current_min == 0):
            hours_list = [19,23]

        order_obj = AssignedOrder.objects.filter(order_assigned_date__year=now.year,
                                                 order_assigned_date__month=now.month,
                                                 order_assigned_date__day=now.day,
                                                 order_assigned_date__hour__range=[hours_list[0],hours_list[1]]).values('total_weight_of_order')
        if not order_obj:
            return True
        else:
            total_weight = 0
            for weight in data:
                total_weight = total_weight + int(weight['order_weight'])
            for weight in order_obj:
                total_weight = total_weight + int(weight['total_weight_of_order'])
            if total_weight > 100:
                return False
            else:
                return True

    @staticmethod
    def check_vehicle_per_day_limit_exceeded():
        now = datetime.datetime.now()
        order_obj = AssignedOrder.objects.filter(order_assigned_date__year=now.year, order_assigned_date__month=now.month,
                                                 order_assigned_date__day=now.day).values('vehicle_type')
        if not order_obj:
            return True, [1, 3, 2]
        else:
            truck_count = 0
            bike_count = 0
            scooter_count = 0
            for order in order_obj:
                if order['vehicle_type'] == "Truck":
                    truck_count = truck_count + 1
                elif order['vehicle_type'] == "Bike":
                    bike_count = bike_count + 1
                elif order['vehicle_type'] == "Scooter":
                    scooter_count = scooter_count + 1
            truck_available = 1 - truck_count
            bike_available = 3 - bike_count
            scooter_count = 2 - scooter_count
            if truck_count > 1 or bike_count > 3 or scooter_count > 2:
                return False, [truck_available, bike_available, scooter_count]
            else:
                return True, [truck_available, bike_available, scooter_count]


    @staticmethod
    def slot_list(current_hour, current_min):
        if (6 <= current_hour < 9) or (current_hour == 9 and current_min == 0):
            return [6,9]
        elif 9 <= current_hour < 13 or (current_hour == 13 and current_min == 0):
            return [9,13]
        elif 16 <= current_hour < 19 or (current_hour == 19 and current_min == 0):
            return [16,19]
        elif 19 <= current_hour <23 or (current_hour == 23 and current_min == 0):
            return [19,23]


    @staticmethod
    def combinational_match_weight(weight, target):
        for we in range(len(weight)):
            if weight[we]['order_weight'] == target:
                return True, weight[we]['order_id'], we

        return False, 0, 0


    @staticmethod
    def total_weight_fun(weight):
        total_weight = 0
        for we in weight:
            total_weight += we['order_weight']
        if total_weight <= 50:
            return False, total_weight
        else:
            return True, total_weight


    def every_vehicle_available(self, weight):
        scooter = []
        truck = []
        bike = []
        i = 0
        flag = False
        while i < len(weight):
            if weight[i]['order_weight'] > 30:
                if weight[i]['order_weight'] < 50:
                    # we can add more weight to this delivery
                    target = 50 - weight[i]['order_weight']
                    exist, order_id, index = self.combinational_match_weight(weight, target)
                    if exist:
                        scooter.append([weight[i]['order_id'], order_id])
                        weight.pop(index)
                        i += 1
                        continue
                    else:
                        scooter.append([weight[i]['order_id']])
                        i += 1
                        continue
                else:
                    scooter.append([weight[i]['order_id']])
                    i += 1
            else:
                current_weight = weight[i]['order_weight']
                current_order_id = []
                first = True
                while i != len(weight) - 1 and current_weight + weight[i + 1]['order_weight'] <= 50:
                    if i == len(weight) - 2:
                        flag = True
                    if first:
                        current_order_id.append(weight[i]["order_id"])
                        first = False
                    current_weight = current_weight + weight[i + 1]['order_weight']
                    current_order_id.append(weight[i + 1]["order_id"])
                    i += 1
                if current_order_id != []:
                    scooter.append(current_order_id)
                else:
                    if flag:
                        i += 1
                        continue
                    bike.append([weight[i]["order_id"]])
                    i += 1
        return truck, scooter, bike


    def order_assignment(self, weight, truckAvailable, bikeAvailable, scooterAvailable):
        weight = sorted(weight, key=lambda i: i['order_weight'], reverse=True)
        # 6-9, truck not allowed, bike/scooter allowed
        bike = []
        scooter = []
        truck = []

        if truckAvailable == True and self.total_weight_fun(weight)[0]:
            truckEffiecent, total_weight = self.total_weight_fun(weight)
            if truckEffiecent:
                # sab truck me bej do
                current_ids = []
                for dic in weight:
                    current_ids.append(dic['order_id'])
                truck.append(current_ids)
                return truck, scooter, bike
            else:
                self.every_vehicle_available(weight)

        elif bikeAvailable == False and scooterAvailable == False and truckAvailable == True:
            current_ids = []
            for dic in weight:
                current_ids.append(dic['order_id'])
            truck.append(current_ids)
            return truck, scooter, bike

        elif weight[0]['order_weight'] > 50 and truckAvailable == False:
            Response({"order_weight": "Since Truck is not available maximum weight that can be handle by scooter i.e 50 and request is exceeding that"},
                     status=status.HTTP_400_BAD_REQUEST)
            return truck,scooter, bike

        else:
            return self.every_vehicle_available(weight)


    def post(self, request, format=None):
        if isinstance(request.data, list):
            # request having multiple object
            serializer = OrderSerializer(data=request.data, many=True)

            # get the current hour when the request has been hit
            now = datetime.datetime.now()
            current_hour = int(now.hour)
            current_min = int(now.minute)
            # current_hour = 6
            # current_min = 2
            if (0 <= current_hour < 6) or 13 < current_hour < 16 or current_hour == 24 or (current_hour == 13 and current_min > 0) or (current_hour == 23 and current_min > 0):
                return Response({"Time": "wrong order timing, please order between 6-9,9-13,16-19,19-23"},
                                status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                slot_weight = self.check_per_slot_100kg(request.data)
                if slot_weight:
                    vehicle_limit_pending_per_day = (self.check_vehicle_per_day_limit_exceeded())[0]
                    if vehicle_limit_pending_per_day:
                        # List of [truck, bike, scooter]
                        vehicle_limit_pending_list_per_day = (self.check_vehicle_per_day_limit_exceeded())[1]
                        weight = request.data
                        weight = sorted(weight, key=lambda we: we['order_weight'], reverse=True)
                        current_slot_list = self.slot_list(current_hour, current_min)


                        if current_slot_list == [6,9]:
                            # order_assignment(self, weight, truckAvailable, bikeAvailable, scooterAvailable):
                            # return truck, scooter, bike
                            if weight[0]['order_weight'] > 50:
                                return Response({
                                    "order_weight": "Since Truck is not available maximum weight that can be handle by scooter i.e 50 and request is exceeding that"},
                                    status=status.HTTP_400_BAD_REQUEST)
                            truck, scooter, bike = self.order_assignment(request.data, False, True, True)
                        elif current_slot_list == [9,13]:
                            truck, scooter, bike = self.order_assignment(request.data, True, True, True)
                        elif current_slot_list == [16,19]:
                            truck, scooter, bike = self.order_assignment(request.data, True, True, True)
                        elif current_slot_list == [19,24]:
                            truck, scooter, bike = self.order_assignment(request.data, True, False, False)

                        bike_delivery_partners = DeliveryPartner.objects.filter(is_available=True, vehicle_type="Bike").values('delivery_partner_id')
                        bike_delivery_partners_list = []
                        if bike_delivery_partners:
                            for i in bike_delivery_partners:
                                bike_delivery_partners_list.append(i['delivery_partner_id'])

                        scooter_delivery_partners = DeliveryPartner.objects.filter(is_available=True,
                                                                                vehicle_type="Scooter").values('delivery_partner_id')
                        scooter_delivery_partners_list = []
                        if scooter_delivery_partners:
                            for i in scooter_delivery_partners:
                                scooter_delivery_partners_list.append(i['delivery_partner_id'])

                        truck_delivery_partners = DeliveryPartner.objects.filter(is_available=True,
                                                                                vehicle_type="Truck").values('delivery_partner_id')

                        truck_delivery_partners_list = []
                        if truck_delivery_partners:
                            for i in truck_delivery_partners:
                                truck_delivery_partners_list.append(i['delivery_partner_id'])

                        assign_data = []
                        if truck != [] or truck != [[]]:
                            if not truck_delivery_partners:
                                return Response({
                                    "delivery partner": "Delivery boy is not available for Truck today"},
                                    status=status.HTTP_400_BAD_REQUEST)
                            for truck_list_iterator in truck:
                                current_truck_dic = {'vehicle_type': "Truck"}
                                if not truck_delivery_partners_list:
                                    return Response({
                                        "delivery partner": "Delivery boy is not available for Truck today"},
                                        status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    current_truck_dic["delivery_partner_id"] = truck_delivery_partners_list[0]
                                    truck_delivery_partners_list.pop(0)
                                    current_truck_dic['list_order_ids_assigned'] = truck_list_iterator
                                assign_data.append(current_truck_dic)
                        if scooter != [] or scooter != [[]]:
                            if not scooter_delivery_partners:
                                return Response({
                                    "delivery partner": "Delivery boy is not available for Truck today"},
                                    status=status.HTTP_400_BAD_REQUEST)
                            for scooter_list_iterator in scooter:
                                current_scooter_dic = {}
                                current_scooter_dic['vehicle_type'] = "Scooter"
                                if not scooter_delivery_partners_list:
                                    return Response({
                                        "delivery partner": "Delivery boy is not available for Scooter today"},
                                        status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    current_scooter_dic["delivery_partner_id"] = scooter_delivery_partners_list[0]
                                    scooter_delivery_partners_list.pop(0)
                                    current_scooter_dic['list_order_ids_assigned'] = scooter_list_iterator
                                assign_data.append(current_scooter_dic)

                        if bike != [] or bike != [[]]:
                            if not bike_delivery_partners:
                                return Response({
                                    "delivery partner": "Delivery boy is not available for Bike today"},
                                    status=status.HTTP_400_BAD_REQUEST)
                            for bike_list_iterator in bike:
                                current_bike_dic = {}
                                current_bike_dic['vehicle_type'] = "Bike"
                                if not bike_delivery_partners_list:
                                    return Response({
                                                    "delivery partner": "Delivery boy is not available for Bike today"},
                                                status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    current_bike_dic["delivery_partner_id"] = bike_delivery_partners_list[0]
                                    bike_delivery_partners_list.pop(0)
                                    current_bike_dic['list_order_ids_assigned'] = bike_list_iterator
                                assign_data.append(current_bike_dic)


                        print("assigned data", assign_data)
                        # example
                        # assign_data = [
                        #     {
                        #         "vehicle_type":"Scooter",
                        #         "delivery_partner_id":15,
                        #         "list_order_ids_assigned": [11],
                        #     }
                        # ]
                        assign_serializer = AssignedOrderSerializer(data=assign_data, many=True)
                        if assign_serializer.is_valid():
                            serializer.save()
                            assign_serializer.save()
                            return Response(assign_data, status=status.HTTP_201_CREATED)

                    else:
                        return Response({"vehicle_limit": "vehicle limit exceeded for today"},
                                        status=status.HTTP_400_BAD_REQUEST)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"slot_weight": "weight exceeded for this slot"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # if orderid already exist
            return Response({"order": "Request is expecting a list of object. For example -  [{order_id: 1, order_weight:30}]"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)
