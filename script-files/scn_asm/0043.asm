0:{
text(1)
op_03E8()
text(2)
op_03EC()
op_03F5()
op_0004()
op_0000()
}

1:{
mov(v120,19)
mov(v121,3)
call(57345,1)
dat_call(68,1)
op_0000()
}

2:{
dat_call(172,1)
op_0004()
op_0000()
}

3:{
call(11:10,1)
op_0004()
op_0000()
}

4:{
op_0004()
op_0000()
}

5:{
op_0004()
op_0000()
}

6:{
op_0004()
op_0000()
}

7:{
op_0004()
op_0000()
}

8:{
op_0004()
op_0000()
}

9:{
op_0004()
op_0000()
}

10:{
op_0004()
op_0000()
}

11:{
test_seen(3157)
msg_reset()
msg_wait_idle()
msg_sync()
op_0402(30)
op_0410(337,11,0)
text(3)
op_03EA()
op_03E8()
text(4)
text(5)
op_03EA()
op_03E8()
text(6)
op_03EC()
op_0412(0,0,11)
msg_reset()
msg_wait_idle()
msg_sync()
op_03F5()
set_seen(3157)
op_0004()
op_0000()
}
