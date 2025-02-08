from django.shortcuts import render
from .models import *
from .serializer import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http.response import Http404
from rest_framework.response import Response
from datetime import datetime, timedelta
from rest_framework import status
from .filters import SiteWorkersFilters
from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework import status
from django_filters import rest_framework as filters
from propertyStatus.models import Project,ProjectType,UnitNo
from bookingForm.models import Booking
from django.db.models import Sum
from django.utils import timezone
from django.db.models import F, Case, When, BooleanField
import pandas as pd
import numpy as np
import io

class SiteWorkersAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return SiteWorkers.objects.get(pk=pk)
        except SiteWorkers.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = SiteWorkersSerializer(data)
                return Response(serializer.data)

            else:
                data = SiteWorkers.objects.filter(deleted=False).order_by('-created_at')
                serializer = SiteWorkersSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            worker_update_date = timezone.now()
            mutable_data['worker_update_date'] = worker_update_date
            serializer = SiteWorkersSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Site Workers Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
        # Get the site workers instance to update
        unit = UnitNo.objects.get(pk=request.data['unit_no'])
        site_workers_to_update = SiteWorkers.objects.get(unit_no=unit, deleted=False)
        try:
            booking  = Booking.objects.get(unit_no=unit)
        except:
            booking  = Booking.objects.filter(unit_no=unit).last()

        total_amount = booking.cost_payable_to_company
        # Get the current time
        current_time = datetime.now()

        # Calculate the time 5 minutes ago
        five_minutes_ago = current_time - timedelta(minutes=5)

        # Check if any worker stage fields are updated
        worker_stages_updated = any([
            site_workers_to_update.worker_stage1,
            site_workers_to_update.worker_stage2,
            site_workers_to_update.worker_stage3,
            site_workers_to_update.worker_stage4,
            site_workers_to_update.worker_stage5,
            site_workers_to_update.worker_stage6,
            site_workers_to_update.worker_stage7
        ])

        worker1 = site_workers_to_update.worker_stage1
        worker2 = site_workers_to_update.worker_stage2
        worker3 = site_workers_to_update.worker_stage3
        worker4 = site_workers_to_update.worker_stage4
        worker5 = site_workers_to_update.worker_stage5
        worker6 = site_workers_to_update.worker_stage6
        worker7 = site_workers_to_update.worker_stage7

        # If worker stages are not updated within the last 60 days, set delay stages to True
        if site_workers_to_update.worker_update_date:
            if (site_workers_to_update.worker_update_date - timezone.now()).total_seconds()/(24*3600) >= 60:
                site_workers_to_update.delay_stage1 = True
                site_workers_to_update.delay_stage2 = True
                site_workers_to_update.delay_stage3 = True
                site_workers_to_update.delay_stage4 = True
                site_workers_to_update.delay_stage5 = True
                site_workers_to_update.delay_stage6 = True
                site_workers_to_update.delay_stage7 = True
        mutable_data = request.data.copy()
        # del mutable_data['total_amount']
        key_str = "".join(mutable_data.keys())
        if 'worker' in key_str:
            worker_update_date = timezone.now()
            mutable_data['worker_update_date'] = worker_update_date
        serializer = SiteWorkersSerializer(instance=site_workers_to_update, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # if request.user.site_worker:
        money = 0
        money_rec = 0
        updated_by = ""
        stage = ""

        if serializer.data['worker_stage1'] and 'worker_stage1' in mutable_data and not worker1:
            money += float(total_amount)*0.25
            stage = 'stage1'
            updated_by = "worker"
        if serializer.data['worker_stage2'] and 'worker_stage2' in mutable_data and not worker2:
            money += float(total_amount)*0.20
            stage = 'stage2'
            updated_by = "worker"

        if serializer.data['worker_stage3'] and 'worker_stage3' in mutable_data and not worker3:
            money += float(total_amount)*0.20
            stage = 'stage3'
            updated_by = "worker"

        if serializer.data['worker_stage4'] and 'worker_stage4' in mutable_data and not worker4:
            money += float(total_amount)*0.10
            stage = 'stage4'
            updated_by = "worker"

        if serializer.data['worker_stage5'] and 'worker_stage5' in mutable_data and not worker5:
            money += float(total_amount)*0.10
            stage = 'stage5'
            updated_by = "worker"

        if serializer.data['worker_stage6'] and 'worker_stage6' in mutable_data  and not worker6:
            money += float(total_amount)*0.10
            stage = 'stage6'
            updated_by = "worker"

        if serializer.data['worker_stage7'] and 'worker_stage7' in mutable_data  and not worker7:
            money += float(total_amount)*0.05
            stage = 'stage7'
            updated_by = "worker"

        if serializer.data['admin_stage1'] and 'admin_stage1' in mutable_data:
            # money += float(total_amount)*0.25
            money_rec += float(request.data['total_rec'])
            stage = 'stage1'
            updated_by = "admin"

        if serializer.data['admin_stage2'] and 'admin_stage2' in mutable_data:
            # money += float(total_amount)*0.20
            money_rec += float(request.data['total_rec'])
            stage = 'stage2'
            updated_by = "admin"

        if serializer.data['admin_stage3'] and 'admin_stage3' in mutable_data:
            # money += float(total_amount)*0.20
            money_rec += float(request.data['total_rec'])
            stage = 'stage3'
            updated_by = "admin"

        if serializer.data['admin_stage4'] and 'admin_stage4' in mutable_data:
            # money += float(total_amount)*0.10
            money_rec += float(request.data['total_rec'])
            stage = 'stage4'
            updated_by = "admin"

        if serializer.data['admin_stage5'] and 'admin_stage5' in mutable_data:
            # money += float(total_amount)*0.10
            money_rec += float(request.data['total_rec'])
            stage = 'stage5'
            updated_by = "admin"

        if serializer.data['admin_stage6'] and 'admin_stage6' in mutable_data:
            # money += float(total_amount)*0.10
            money_rec += float(request.data['total_rec'])
            stage = 'stage6'
            updated_by = "admin"

        if serializer.data['admin_stage7'] and 'admin_stage7' in mutable_data:
            # money += float(total_amount)*0.05
            money_rec += float(request.data['total_rec'])
            stage = 'stage7'
            updated_by = "admin"

        expense_serialier = MonthlyExpenseSerializer(data={"money":money,"money_rec":money_rec,"siteworker":serializer.data['id'], "stage":stage, "updated_by":updated_by})
        if not expense_serialier.is_valid():
            print(expense_serialier.errors)
        expense_serialier.save()

        response_data = {
            'message': 'Site Workers updated successfully',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    def delete(self, request, pk, format=None):
        SiteWorkers_to_delete =  SiteWorkers.objects.get(pk=pk)

            # delete the todo
        SiteWorkers_to_delete.delete()

        return Response({
            'message': 'Site Workers Deleted Successfully'
        })
    



class SiteWorkersData(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SiteWorkers.objects.filter(deleted=False)
    serializer_class = SiteWorkersSerializer
    filter_backends = [filters.DjangoFilterBackend,SearchFilter]
    filterset_class = SiteWorkersFilters
    search_fields = [ 'project_name', 'unit_no']
    ordering_fields = ['final_amount', 'worker_update_date']

    def get_queryset(self):
        # Annotate a new field 'accept_first' to prioritize records with accept=True
        queryset = super().get_queryset().annotate(
            accept_first=Case(
                When(accept=True, then=1),
                default=0,
                output_field=BooleanField()
            ),
        target_priority=Case(
            When(target=True, then=1),
            default=0,
            output_field=BooleanField()
        )
        ).order_by(
        '-accept_first',  # Order by accept priority first
        '-target_priority',  # Then order by target priority
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # Apply additional filtering based on final_amount_min and final_amount_max
        final_amount_min = request.query_params.get('final_amount_min')
        final_amount_max = request.query_params.get('final_amount_max')

        if final_amount_min is not None or final_amount_max is not None:
            filtered_queryset = []

            for instance in queryset:
                serialized_data = SiteWorkersSerializer(instance).data
                final_amount = serialized_data.get('final_amount')

                if (float(final_amount_min) <= final_amount) and (float(final_amount_max) >= final_amount):
                    filtered_queryset.append(instance)

            # Calculate target summary
        # target_records = queryset.filter(target=True)
        # target_amount = 0
        # target_amount_raised = 0

        # for record in target_records:
        #     total_amount = record.unit_no.unit_cost
            
        #     if record.target:
        #         target_amount += total_amount
                
        #         # Calculate total_rec based on the MonthlyExpense
        #         all_money = MonthlyExpense.objects.filter(siteworker=record, deleted=False).values('stage').annotate(
        #             total_money=Sum('money'),
        #             total_money_rec=Sum('money_rec')
        #         )
                
        #         for expense_group in all_money:
        #             stage = expense_group['stage']
        #             total_money_rec = expense_group['total_money_rec']
                    
        #             # Add to target_amount_raised if this stage matches the record's stage_name
        #             if record.stage_name == f"Stage {stage[-1]}":  # Assumes stage names are like "Stage 1", "Stage 2", etc.
        #                 target_amount_raised += total_money_rec

        # target_summary = {
        #     'target_amount': target_amount,
        #     'target_amount_raised': target_amount_raised
        # }

        

        expenses = []
        if not queryset.exists():
            try:
                # print({"project_name":int(request.GET.get("project_name")), "unit_no":int(request.GET.get("unit_no"))})
                try:
                    queryset = SiteWorkers.objects.get(project_name=Project.objects.get(pk=int(request.GET.get("project_name"))), unit_no=UnitNo.objects.get(unit_no=request.GET.get("unit_no")), deleted=False)
                    workerSerializer = SiteWorkersSerializer(queryset)
                    all_money = MonthlyExpense.objects.filter(siteworker=queryset.id, updated_by='admin', deleted=False).values('stage').annotate(
                                    total_money=Sum('money'),
                                    total_money_rec=Sum('money_rec')
                                )
                    try:
                        booking  = Booking.objects.get(unit_no=queryset.unit_no, deleted=False, cancelled=False)
                    except:
                        booking  = Booking.objects.filter(unit_no=queryset.unit_no, deleted=False, cancelled=False).last()

                    total_amount = booking.cost_payable_to_company
                    expenses = {}
                    stages = [f'stage{i}' for i in range(1,8)]

                    for expense_group in all_money:
                        stage = expense_group['stage']
                        if stage in stages:
                            stages.remove(stage)
                        total_money = expense_group['total_money']
                        total_money_rec = expense_group['total_money_rec']
                        expenses[stage]={"total":total_money, "total_rec":total_money_rec}
                    for stage in stages:
                        if '1' in stage:
                            money = float(total_amount)*0.25
                        elif '2' in stage:
                            money = float(total_amount)*0.20
                        elif '3' in stage:
                            money = float(total_amount)*0.20
                        elif '4' in stage:
                            money = float(total_amount)*0.10
                        elif '5' in stage:
                            money = float(total_amount)*0.10
                        elif '6' in stage:
                            money = float(total_amount)*0.10
                        elif '7' in stage:
                            money = float(total_amount)*0.05
                        expenses[stage]={"total":money, "total_rec":0}
                    data = workerSerializer.data.copy()
                    workerSerializer.data['expense'] = expenses
                except:
                    print({"project_name":Project.objects.get(id=int(request.GET.get("project_name")), deleted=False), "unit_no":UnitNo.objects.get(unit_no=request.GET.get("unit_no"))})
                    workerSerializer = SiteWorkersSerializer(data={"project_name":Project.objects.get(id=int(request.GET.get("project_name")), deleted=False), "unit_no":UnitNo.objects.get(unit_no=request.GET.get("unit_no"))})
                    workerSerializer.is_valid(raise_exception=True)
                    workerSerializer.save()
                    obj = SiteWorkers.objects.get(pk=workerSerializer.data['id'], deleted=False)
                    obj.project_name = Project.objects.get(id=int(request.GET.get("project_name")), deleted=False)
                    obj.save()
                    data = workerSerializer.data.copy()
                    data['expense'] = {}
                return Response([data])
            except Exception as e:
                print(e)
                return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)
        
        expenses = []
        for qry in queryset:
            if timezone.is_naive(qry.updated_at):
                updated_at = timezone.make_aware(qry.updated_at, timezone.get_current_timezone())
            else:
                updated_at = qry.updated_at
                
            if (datetime.now()-qry.updated_at).days>=60:
                if not qry.worker_stage1:
                    qry.delay_stage1 = True
                elif not qry.worker_stage2:
                    qry.delay_stage2 = True
                elif not qry.worker_stage3:
                    qry.delay_stage2 = True
                elif not qry.worker_stage4:
                    qry.delay_stage2 = True
                elif not qry.worker_stage5:
                    qry.delay_stage2 = True
                elif not qry.worker_stage6:
                    qry.delay_stage2 = True
                elif not qry.worker_stage7:
                    qry.delay_stage2 = True
                qry.updated_at = datetime.now()
                qry.save()
            try:
                booking  = Booking.objects.get(unit_no=qry.unit_no, deleted=False, cancelled=False)
            except:
                booking  = Booking.objects.filter(unit_no=qry.unit_no, deleted=False, cancelled=False).last()
            if booking:
                total_amount = booking.cost_payable_to_company
                expense = {}
                try:
                    all_money = MonthlyExpense.objects.filter(siteworker=qry, deleted=False).values('stage').annotate(
                                            total_money=Sum('money'),
                                            total_money_rec=Sum('money_rec')
                                        )
                    stages = [f'stage{i}' for i in range(1,8)]
                    for expense_group in all_money:
                        stage = expense_group['stage']
                        if stage in stages:
                            stages.remove(stage)
                        total_money = expense_group['total_money']
                        total_money_rec = expense_group['total_money_rec']
                        expense[stage]={"total":total_money, "total_rec":total_money_rec}
                    print(stages)
                    for stage in stages:
                        print('2' in stage)
                        if '1' in stage:
                            money = float(total_amount)*0.25
                        elif '2' in stage:
                            money = float(total_amount)*0.20
                        elif '3' in stage:
                            money = float(total_amount)*0.20
                        elif '4' in stage:
                            money = float(total_amount)*0.10
                        elif '5' in stage:
                            money = float(total_amount)*0.10
                        elif '6' in stage:
                            money = float(total_amount)*0.10
                        elif '7' in stage:
                            money = float(total_amount)*0.05
                        expense[stage]={"total":money, "total_rec":0}

                except Exception as e:
                    print(e, "last")
                expenses.append(expense)
        # print(expenses)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data.copy()
        for d, e in zip(data, expenses):
            d['expense'] = e
        
        # Include the target summary in the response

        return Response(data)


class SiteWorkersDataTotalReciviedTargetAmount(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SiteWorkers.objects.filter(deleted=False)
    serializer_class = SiteWorkersSerializer
    filterset_class = SiteWorkersFilters

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # Apply additional filtering based on final_amount_min and final_amount_max

            # Calculate target summary
        target_records = queryset.filter(target=True)
        target_amount = 0
        target_amount_raised = 0

        for record in target_records:
            total_amount = record.unit_no.unit_cost
            
            if record.target:
                target_amount += total_amount
                
                # Calculate total_rec based on the MonthlyExpense
                all_money = MonthlyExpense.objects.filter(siteworker=record, deleted=False).values('stage').annotate(
                    total_money=Sum('money'),
                    total_money_rec=Sum('money_rec')
                )
                
                for expense_group in all_money:
                    stage = expense_group['stage']
                    total_money_rec = expense_group['total_money_rec']
                    
                    if stage and len(stage) > 0:
                        try:
                            stage_number = int(stage[-1])
                        except ValueError:
                            continue  # Skip if the stage does not end with a number

                        if record.stage_name == f"Stage {stage_number}":
                            target_amount_raised += total_money_rec

        target_summary = {
            'target_amount': target_amount,
            'target_amount_raised': target_amount_raised
        }

        

        expenses = []

        if not queryset.exists():
            try:
                # print({"project_name":int(request.GET.get("project_name")), "unit_no":int(request.GET.get("unit_no"))})
                try:
                    queryset = SiteWorkers.objects.get(project_name=Project.objects.get(pk=int(request.GET.get("project_name"))), unit_no=UnitNo.objects.get(unit_no=request.GET.get("unit_no")), deleted=False)
                    workerSerializer = SiteWorkersSerializer(queryset)
                    all_money = MonthlyExpense.objects.filter(siteworker=queryset.id, updated_by='admin', deleted=False).values('stage').annotate(
                                    total_money=Sum('money'),
                                    total_money_rec=Sum('money_rec')
                                )
                    try:
                        booking  = Booking.objects.get(unit_no=queryset.unit_no, deleted=False, cancelled=False)
                    except:
                        booking  = Booking.objects.filter(unit_no=queryset.unit_no, deleted=False, cancelled=False).last()

                    total_amount = booking.cost_payable_to_company
                    expenses = {}
                    stages = [f'stage{i}' for i in range(1,8)]

                    for expense_group in all_money:
                        stage = expense_group['stage']
                        if stage in stages:
                            stages.remove(stage)
                        total_money = expense_group['total_money']
                        total_money_rec = expense_group['total_money_rec']
                        expenses[stage]={"total":total_money, "total_rec":total_money_rec}
                    for stage in stages:
                        if '1' in stage:
                            money = float(total_amount)*0.25
                        elif '2' in stage:
                            money = float(total_amount)*0.20
                        elif '3' in stage:
                            money = float(total_amount)*0.20
                        elif '4' in stage:
                            money = float(total_amount)*0.10
                        elif '5' in stage:
                            money = float(total_amount)*0.10
                        elif '6' in stage:
                            money = float(total_amount)*0.10
                        elif '7' in stage:
                            money = float(total_amount)*0.05
                        expenses[stage]={"total":money, "total_rec":0}
                    data = workerSerializer.data.copy()
                    workerSerializer.data['expense'] = expenses
                except:
                    print({"project_name":Project.objects.get(id=int(request.GET.get("project_name")), deleted=False), "unit_no":UnitNo.objects.get(unit_no=request.GET.get("unit_no"))})
                    workerSerializer = SiteWorkersSerializer(data={"project_name":Project.objects.get(id=int(request.GET.get("project_name")), deleted=False), "unit_no":UnitNo.objects.get(unit_no=request.GET.get("unit_no"))})
                    workerSerializer.is_valid(raise_exception=True)
                    workerSerializer.save()
                    obj = SiteWorkers.objects.get(pk=workerSerializer.data['id'], deleted=False)
                    obj.project_name = Project.objects.get(id=int(request.GET.get("project_name")), deleted=False)
                    obj.save()
                    data = workerSerializer.data.copy()
                    data['expense'] = {}
                return Response([data])
            except Exception as e:
                print(e)
                return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)
        
        expenses = []
        for qry in queryset:
            if timezone.is_naive(qry.updated_at):
                updated_at = timezone.make_aware(qry.updated_at, timezone.get_current_timezone())
            else:
                updated_at = qry.updated_at
                
            if (datetime.now()-qry.updated_at).days>=60:
                if not qry.worker_stage1:
                    qry.delay_stage1 = True
                elif not qry.worker_stage2:
                    qry.delay_stage2 = True
                elif not qry.worker_stage3:
                    qry.delay_stage2 = True
                elif not qry.worker_stage4:
                    qry.delay_stage2 = True
                elif not qry.worker_stage5:
                    qry.delay_stage2 = True
                elif not qry.worker_stage6:
                    qry.delay_stage2 = True
                elif not qry.worker_stage7:
                    qry.delay_stage2 = True
                qry.updated_at = datetime.now()
                qry.save()
            try:
                booking  = Booking.objects.get(unit_no=qry.unit_no, deleted=False, cancelled=False)
            except:
                booking  = Booking.objects.filter(unit_no=qry.unit_no, deleted=False, cancelled=False).last()
            if booking:
                total_amount = booking.cost_payable_to_company
                expense = {}
                try:
                    all_money = MonthlyExpense.objects.filter(siteworker=qry, deleted=False).values('stage').annotate(
                                            total_money=Sum('money'),
                                            total_money_rec=Sum('money_rec')
                                        )
                    stages = [f'stage{i}' for i in range(1,8)]
                    for expense_group in all_money:
                        stage = expense_group['stage']
                        if stage in stages:
                            stages.remove(stage)
                        total_money = expense_group['total_money']
                        total_money_rec = expense_group['total_money_rec']
                        expense[stage]={"total":total_money, "total_rec":total_money_rec}
                    print(stages)
                    for stage in stages:
                        print('2' in stage)
                        if '1' in stage:
                            money = float(total_amount)*0.25
                        elif '2' in stage:
                            money = float(total_amount)*0.20
                        elif '3' in stage:
                            money = float(total_amount)*0.20
                        elif '4' in stage:
                            money = float(total_amount)*0.10
                        elif '5' in stage:
                            money = float(total_amount)*0.10
                        elif '6' in stage:
                            money = float(total_amount)*0.10
                        elif '7' in stage:
                            money = float(total_amount)*0.05
                        expense[stage]={"total":money, "total_rec":0}

                except Exception as e:
                    print(e, "last")
                expenses.append(expense)
        # print(expenses)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data.copy()
        for d, e in zip(data, expenses):
            d['expense'] = e
        
        response_data = {
            'target_summary': target_summary,
        }

        return Response(response_data)

class GetExpense(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return MonthlyExpense.objects.get(pk=pk, deleted=False)
        except MonthlyExpense.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if pk:
            data = self.get_object(pk)
            serializer = MonthlyExpenseSerializer(data)
            return Response(serializer.data)

        elif start_date and end_date:
            queryset = MonthlyExpense.objects.filter(created_at__gte=start_date, created_at__lte=end_date, deleted=False)
            serializer = MonthlyExpenseSerializer(queryset, many=True)
            total = 0
            total_rec = 0
            for i in serializer.data:
                total += i['money']
                if i['money_rec']:
                    total_rec += float(i['money_rec'])
            return Response({"records":serializer.data, "total":total, "total_rec":total_rec}, status=status.HTTP_200_OK)
        elif start_date:
            queryset = MonthlyExpense.objects.filter(created_at__gte=start_date, deleted=False)
            serializer = MonthlyExpenseSerializer(queryset, many=True)
            total = 0
            total_rec = 0
            for i in serializer.data:
                total += i['money']
                if i['money_rec']:
                    total_rec += float(i['money_rec'])
            return Response({"records":serializer.data, "total":total, "total_rec":total_rec}, status=status.HTTP_200_OK)
        elif end_date:
            queryset = MonthlyExpense.objects.filter(created_at__lte=end_date, deleted=False)
            serializer = MonthlyExpenseSerializer(queryset, many=True)
            total = 0
            total_rec = 0
            for i in serializer.data:
                total += i['money']
                if i['money_rec']:
                    total_rec += float(i['money_rec'])
            return Response({"records":serializer.data, "total":total, "total_rec":total_rec}, status=status.HTTP_200_OK)
        else:
            now = datetime.now()

            current_year = now.year
            current_month = now.month

            queryset = MonthlyExpense.objects.filter(
                # created_at__year=current_year,
                # created_at__month=current_month,
                deleted=False
            )
            serializer = MonthlyExpenseSerializer(queryset, many=True)
            total = 0
            total_rec = 0
            for i in serializer.data:
                total += i['money']
                if i['money_rec']:
                    total_rec += float(i['money_rec'])
            return Response({"records":serializer.data, "total":total, "total_rec":total_rec}, status=status.HTTP_200_OK)

class SiteWorkerFile(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date and end_date:
            queryset = MonthlyExpense.objects.filter(created_at__gte=start_date, created_at__lte=end_date, deleted=False)
        
        elif start_date:
            queryset = MonthlyExpense.objects.filter(created_at__gte=start_date, deleted=False)
        
        elif end_date:
            queryset = MonthlyExpense.objects.filter(created_at__lte=end_date, deleted=False)
        
        else:
            now = datetime.now()

            # Get the current year and month
            current_year = now.year
            current_month = now.month

            # Filter the queryset
            queryset = MonthlyExpense.objects.filter(
                # created_at__year=current_year,
                # created_at__month=current_month,
                deleted=False
            )
        
        df = pd.DataFrame(columns=["project","unit no","stage 1","stage 1_1","stage 1_date","stage 2","stage 2_2","stage 2_date","stage 3","stage 3_3","stage 3_date",
        "stage 4","stage 4_4","stage 4_date","stage 5","stage 5_5","stage 5_date","stage 6","stage 6_6","stage 6_date","stage 7","stage 7_7","stage 7_date"])
        df.loc[len(df)] = ["",""]+["Amount to be raised", "Amount raised",""]*7
        for i in queryset:
            if len(df[df['unit no']==i.siteworker.unit_no.unit_no])>0:
                if i.stage:
                    stage = i.stage[-1]
                    df.loc[(df['unit no']==i.siteworker.unit_no.unit_no),'stage '+stage] += i.money 
                    df.loc[(df['unit no']==i.siteworker.unit_no.unit_no),'stage '+stage+'_'+stage] += i.money_rec 
                    df.loc[(df['unit no']==i.siteworker.unit_no.unit_no),'stage '+stage+'_date'] = i.updated_at
            else:
                stage = i.stage[-1]
                row = [np.nan]*((int(stage)-1)*3) + [i.money, i.money_rec, i.updated_at] + [np.nan]*((7-int(stage))*3)

                df.loc[len(df)] = [i.siteworker.project_name.project_name,i.siteworker.unit_no.unit_no]+row
        
        output = io.BytesIO()
        col_dict = {}
        for i in range(1,8):
            col_dict[f"stage {i}_{i}"] = f"stage {i}"
            col_dict[f"stage {i}_date"] = f"Date"

        df.rename(columns=col_dict, inplace=True)
        print(df, col_dict)
        # Write to an Excel file
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='SiteWorkerData')
            workbook = writer.book
            worksheet = writer.sheets['SiteWorkerData']
            
            # Format the columns
            for idx, column in enumerate(df.columns):
                print(f"Setting column width for index: {idx}, column name: {column}")
                worksheet.set_column(idx, idx, 15)

        # Seek to the beginning of the BytesIO buffer
        output.seek(0)

        # Create the HTTP response
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="SiteWorkerData.xlsx"'
        return response

class SiteVisitPatchAPIview(APIView):
    permission_classes = [IsAuthenticated]    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        site_worker_deatils_to_update = SiteWorkers.objects.get(pk=pk)

        serializer = SiteWorkersSerializer(instance=site_worker_deatils_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'site worker updated Successfully',
            'data': serializer.data
        }

        return response