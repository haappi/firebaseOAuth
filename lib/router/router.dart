import 'package:flutter/cupertino.dart';
import 'package:go_router/go_router.dart';

GoRouter _router = GoRouter(
  navigatorKey: GlobalKey<NavigatorState>(),
  initialLocation: '/',
  routes: [],

);